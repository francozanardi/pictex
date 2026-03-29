from ..font_manager import FontManager
from ...models import Style, LineMetrics, TextRun, FontMetrics, TextBoxEdge, TextBoxEdgeValue, LineHeightMode
from .metrics_strategy import AggregatedLineFontsMetrics, LineMetricsStrategy
from .font_metrics_strategy import FontMetricsStrategy
from .glyphs_metrics_strategy import GlyphsMetricsStrategy


class LineMetricsCalculator:
    """Computes LineMetrics for a shaped text line.

    Acts as the entry point for line sizing. It reads the ``text_box_edge``
    style property to select the appropriate strategy for each edge, then
    delegates the actual calculation.
    """

    def __init__(self, style: Style, font_manager: FontManager):
        self._style = style
        self._font_manager = font_manager

    def calculate(self, runs: list[TextRun], font_metrics: list[FontMetrics]) -> LineMetrics:
        """Calculate LineMetrics for a line composed of the given runs.

        Args:
            runs: Shaped TextRuns that form the line (shaped_glyphs must already be set).
            font_metrics: Font metrics for every font used in the line.

        Returns:
            LineMetrics describing the line box dimensions and key positions.
        """
        aggregated_metrics = self._aggregate_font_metrics(font_metrics)
        edge: TextBoxEdge = self._style.text_box_edge.get()
        top_metrics = self._calculate_metrics_for_edge(edge.top, runs, aggregated_metrics)
        bottom_metrics = self._calculate_metrics_for_edge(edge.bottom, runs, aggregated_metrics)
        return self._merge_strategies(top_metrics, bottom_metrics)
    
    def _aggregate_font_metrics(self, font_metrics: list[FontMetrics]) -> AggregatedLineFontsMetrics:
        """Aggregate font metrics across all fonts in the line."""
        ascent = max(m.ascent for m in font_metrics)
        descent = max(m.descent for m in font_metrics)
        leading = max(m.leading for m in font_metrics)
        vertical_space = self._vertical_space(ascent, descent, leading)
        underline_from_top = self._underline_from_top(font_metrics)
        strikethrough_from_top = self._strikethrough_from_top()
        return AggregatedLineFontsMetrics(
            ascent=ascent,
            descent=descent,
            vertical_space=vertical_space,
            underline_from_top=underline_from_top,
            strikethrough_from_top=strikethrough_from_top
        )

    def _underline_from_top(self, font_metrics: list[FontMetrics]) -> float:
        """Return the underline position as a distance from the top of the line."""
        return max(m.ascent + m.underline_position for m in font_metrics)

    def _strikethrough_from_top(self) -> float:
        """Return the strikethrough position as distance from the top of the line."""
        primary_font_metrics = self._font_manager.get_font_metrics(self._font_manager.get_primary_font())
        return primary_font_metrics.ascent + primary_font_metrics.strikethrough_position

    def _vertical_space(self, ascent: float, descent: float, leading: float) -> float:
        """Compute the extra vertical padding per edge from ``line_height``."""
        line_height_style = self._style.line_height.get()

        if line_height_style.mode == LineHeightMode.MULTIPLIER:
            physical_height = ascent + descent
            user_height = line_height_style.value * self._style.font_size.get()
            return (user_height - physical_height) / 2

        if line_height_style.mode == LineHeightMode.AUTO:
            return leading / 2

        raise ValueError(f"Unsupported line height mode: {line_height_style.mode}")
    
    def _calculate_metrics_for_edge(
        self, edge_value: TextBoxEdgeValue, runs: list[TextRun], aggregated_metrics: AggregatedLineFontsMetrics
    ) -> LineMetrics:
        """Calculate LineMetrics for a single edge using the specified strategy."""
        strategy = self._build_strategy(edge_value)
        return strategy.calculate(runs, aggregated_metrics)

    def _build_strategy(self, edge_value: TextBoxEdgeValue) -> LineMetricsStrategy:
        if edge_value == TextBoxEdgeValue.GLYPHS:
            return GlyphsMetricsStrategy()
        
        if edge_value == TextBoxEdgeValue.FONT:
            return FontMetricsStrategy()
        
        raise ValueError(f"Unsupported TextBoxEdgeValue: {edge_value}")

    def _merge_strategies(
        self, top_metrics: LineMetrics, bottom_metrics: LineMetrics
    ) -> LineMetrics:
        """Run both strategies and merge into a single LineMetrics.

        The top strategy owns the baseline, underline and strikethrough positions.
        The bottom strategy owns how far the box extends below the baseline.
        Each strategy independently decides whether to apply ``vertical_space``.
        """
        bottom_extent = bottom_metrics.height - bottom_metrics.baseline

        return LineMetrics(
            height=top_metrics.baseline + bottom_extent,
            baseline=top_metrics.baseline,
            underline=top_metrics.underline,
            strikethrough=top_metrics.strikethrough,
        )
