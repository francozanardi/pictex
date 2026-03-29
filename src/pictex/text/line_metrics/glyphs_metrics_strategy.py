from typing import Optional
import skia
from ...models import LineMetrics, TextRun, ShapedGlyph
from .metrics_strategy import AggregatedLineFontsMetrics, LineMetricsStrategy


class GlyphsMetricsStrategy(LineMetricsStrategy):
    """Sizes the line box using the actual ink bounds of the rendered glyphs.

    Instead of relying on fixed font metrics (ascent/descent), this strategy
    measures how far up and down the glyphs actually extend. The resulting box
    tightly wraps the visible ink, removing empty space reserved for characters
    that are not present in the string.

    Trade-off: the box height is content-dependent. Different strings may
    produce different line heights, which can shift surrounding layout elements.
    Use this strategy only when you control the text content and need the
    tightest possible fit.
    """

    def calculate(
        self,
        runs: list[TextRun],
        metrics: AggregatedLineFontsMetrics
    ) -> LineMetrics:
        ink_ascent, ink_descent = self._measure_ink_bounds(runs)

        # Fall back to font metrics when no ink is found (e.g. whitespace-only lines).
        ascent = ink_ascent if ink_ascent is not None else metrics.ascent
        descent = ink_descent if ink_descent is not None else metrics.descent

        # Glyphs strategy does not apply vertical_space - the user explicitly
        # asked for the box to hug the ink bounds with no extra padding.
        height = ascent + descent

        return LineMetrics(
            height=height,
            baseline=ascent,
            underline=metrics.underline_from_top,
            strikethrough=metrics.strikethrough_from_top,
        )

    def _measure_ink_bounds(
        self, runs: list[TextRun]
    ) -> tuple[Optional[float], Optional[float]]:
        """Return the maximum (ink_ascent, ink_descent) across all glyphs in all runs.

        Ink bounds are measured directly from the font via ``skia.Font.getBounds()``,
        which returns each glyph's bounding box relative to its origin (the baseline).
        ``bounds.top`` is negative when the glyph rises above the baseline (normal case),
        and ``bounds.bottom`` is positive when it descends below.

        Returns (None, None) if no ink is found (e.g. a whitespace-only line).
        """
        max_ink_ascent: Optional[float] = None
        max_ink_descent: Optional[float] = None

        for run in runs:
            if not run.shaped_glyphs:
                continue
            for bounds in self._get_glyph_bounds(run.shaped_glyphs, run.font):
                ink_ascent = max(0.0, -bounds.top())
                ink_descent = max(0.0, bounds.bottom())

                if max_ink_ascent is None or ink_ascent > max_ink_ascent:
                    max_ink_ascent = ink_ascent
                if max_ink_descent is None or ink_descent > max_ink_descent:
                    max_ink_descent = ink_descent

        return max_ink_ascent, max_ink_descent

    def _get_glyph_bounds(
        self, glyphs: list[ShapedGlyph], font: skia.Font
    ) -> list[skia.Rect]:
        """Return per-glyph ink bounding boxes from Skia, skipping empty bounds."""
        glyph_ids = [g.glyph_id for g in glyphs]
        all_bounds = font.getBounds(glyph_ids)
        return [b for b in all_bounds if not b.isEmpty()]
