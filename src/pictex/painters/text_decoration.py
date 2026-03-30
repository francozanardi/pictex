from typing import Optional
from .painter import Painter
from ..text import FontManager
from ..utils import get_line_x_position
from ..models import TextDecoration, Style, Line
import skia

class DecorationPainter(Painter):

    def __init__(self, style: Style, font_manager: FontManager, text_bounds: skia.Rect, lines: list[Line]):
        super().__init__(style)
        self._font_manager = font_manager
        self._text_bounds = text_bounds
        self._lines = lines

    def paint(self, canvas: skia.Canvas) -> None:
        current_y = self._text_bounds.top()
        block_width = self._text_bounds.width()

        for line in self._lines:
            if not line.runs:
                current_y += line.metrics.height
                continue

            line_x_start = self._text_bounds.x() + get_line_x_position(line.width, block_width, self._style.text_align.get())
            span_bounds = self._compute_span_bounds(line, line_x_start, current_y)
            self._draw_merged_decorations(canvas, line.runs, line_x_start, current_y + line.metrics.underline, 'underline', span_bounds)
            self._draw_merged_decorations(canvas, line.runs, line_x_start, current_y + line.metrics.strikethrough, 'strikethrough', span_bounds)

            current_y += line.metrics.height

    def _compute_span_bounds(self, line: Line, line_x_start: float, current_y: float) -> dict:
        span_bounds = {}
        x = line_x_start
        for run in line.runs:
            sid = id(run.span)
            rb = skia.Rect.MakeXYWH(x, current_y, run.width, line.metrics.height)
            if sid not in span_bounds:
                span_bounds[sid] = rb
            else:
                e = span_bounds[sid]
                span_bounds[sid] = skia.Rect.MakeLTRB(
                    min(e.left(), rb.left()), min(e.top(), rb.top()),
                    max(e.right(), rb.right()), max(e.bottom(), rb.bottom()),
                )
            x += run.width
        return span_bounds

    def _draw_merged_decorations(self, canvas: skia.Canvas, runs: list, line_x_start: float, line_y: float, attr: str, span_bounds: dict) -> None:
        """Draw decorations for a line, merging consecutive runs with the same decoration into
        a single drawLine call to avoid sub-pixel seams at run boundaries.

        Internal boundaries between adjacent segments are snapped to integer pixels to prevent
        AA coverage overlap (because of subpixels). The outer edges (start of first segment, end of last) are left at
        their natural float positions since there is no adjacent segment to conflict with.

        Runs from different spans are only merged when the decoration has an explicit color;
        if the fallback span color is used, each span forms its own segment to preserve correct gradient bounds.
        """
        segments: list[tuple[float, float, object, object]] = []
        current_x = line_x_start
        seg_x = None
        seg_decoration = None
        seg_span = None

        for run in runs:
            decoration = getattr(run.style, attr).get()
            extends = (
                decoration == seg_decoration and
                (decoration is None or decoration.color is not None or run.span is seg_span)
            )

            if not extends:
                if seg_decoration is not None:
                    segments.append((seg_x, current_x, seg_decoration, seg_span))
                seg_decoration = decoration
                seg_span = run.span if decoration is not None else None
                seg_x = current_x if decoration is not None else None
            current_x += run.width

        if seg_decoration is not None:
            segments.append((seg_x, current_x, seg_decoration, seg_span))

        for i, (x_start, x_end, decoration, span_info) in enumerate(segments):
            is_first = i == 0
            is_last = i == len(segments) - 1
            x0 = x_start if is_first else round(x_start)
            x1 = x_end if is_last else round(x_end)
            self._draw_decoration(canvas, decoration, x0, line_y, x1 - x0, span_info, span_bounds)

    def _draw_decoration(
            self,
            canvas: skia.Canvas,
            decoration: Optional[TextDecoration],
            line_x_start: float,
            line_y: float,
            line_width: float,
            span_info,
            span_bounds: dict,
    ) -> None:
        if not decoration:
            return

        paint = skia.Paint(AntiAlias=True, StrokeWidth=decoration.thickness)
        half_thickness = decoration.thickness / 2
        if decoration.color:
            color = decoration.color
            bounds = skia.Rect.MakeLTRB(
                line_x_start,
                line_y - half_thickness,
                line_x_start + line_width,
                line_y + half_thickness
            )
            color.apply_to_paint(paint, bounds)
        else:
            color = span_info.computed_style.color.get()
            if span_info.explicit_style and span_info.explicit_style.is_explicit('color'):
                bounds = span_bounds[id(span_info)]
            else:
                bounds = self._text_bounds
            color.apply_to_paint(paint, bounds)

        canvas.drawLine(line_x_start, line_y, line_x_start + line_width, line_y, paint)
