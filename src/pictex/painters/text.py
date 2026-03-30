from .painter import Painter
from ..text import FontManager
from ..utils import create_composite_shadow_filter, get_line_x_position
import skia
from ..models import Style, Line, PaintSource, StrokeMode

class TextPainter(Painter):

    def __init__(
            self,
            style: Style,
            font_manager: FontManager,
            text_bounds: skia.Rect,
            parent_bounds: skia.Rect,
            lines: list[Line],
            is_svg: bool
    ):
        super().__init__(style)
        self._font_manager = font_manager
        self._text_bounds = text_bounds
        self._parent_bounds = parent_bounds
        self._is_svg = is_svg
        self._lines: list[Line] = lines

    def paint(self, canvas: skia.Canvas) -> None:
        self._draw_text(canvas)

    def _draw_text(self, canvas: skia.Canvas) -> None:
        current_y = self._text_bounds.top()
        block_width = self._parent_bounds.width()

        for line in self._lines:
            draw_x_start = self._text_bounds.x() + get_line_x_position(line.width, block_width, self._style.text_align.get())
            current_x = draw_x_start

            span_bounds = self._compute_span_bounds(line, draw_x_start, current_y)

            for run in line.runs:
                run_bounds = skia.Rect.MakeXYWH(current_x, current_y, run.width, line.metrics.height)
                color_bounds = self._paint_bounds(run, 'color', span_bounds)
                stroke_bounds = self._paint_bounds(run, 'text_stroke', span_bounds)

                fill_paint = skia.Paint(AntiAlias=True)
                run.style.color.get().apply_to_paint(fill_paint, color_bounds)
                self._add_shadows_to_paint(fill_paint, run.style)

                blob = run.blob if run.blob else skia.TextBlob.MakeFromShapedText(run.text, run.font)
                self._render_text_blob(canvas, blob, current_x, current_y, fill_paint, run.style, run_bounds, stroke_bounds)
                current_x += run.width

            current_y += line.metrics.height

    def _compute_span_bounds(self, line: Line, draw_x_start: float, current_y: float) -> dict:
        span_bounds = {}
        x = draw_x_start
        for run in line.runs:
            rb = skia.Rect.MakeXYWH(x, current_y, run.width, line.metrics.height)
            if run.span.explicit_style:
                for field_name in run.span.explicit_style.get_field_names():
                    property_obj = getattr(run.span.explicit_style, field_name)
                    if property_obj.was_set:
                        pid = property_obj.origin_id
                        if pid not in span_bounds:
                            span_bounds[pid] = rb
                        else:
                            e = span_bounds[pid]
                            span_bounds[pid] = skia.Rect.MakeLTRB(
                                min(e.left(), rb.left()), min(e.top(), rb.top()),
                                max(e.right(), rb.right()), max(e.bottom(), rb.bottom()),
                            )
            x += run.width
        return span_bounds

    def _paint_bounds(self, run, prop: str, span_bounds: dict) -> skia.Rect:
        """Return the correct bounds for apply_to_paint.

        If the property was explicitly set on the run's span, use the span's
        bounds (union of all co-span runs on this line) so the gradient covers
        the full span extent. Otherwise fall back to the full text block bounds,
        preserving the pre-feature behavior for block-level gradients.
        """
        if run.span.explicit_style and run.span.explicit_style.is_explicit(prop):
            property_obj = getattr(run.span.explicit_style, prop)
            return span_bounds[property_obj.origin_id]
        return self._text_bounds

    def _add_shadows_to_paint(self, paint: skia.Paint, style: Style) -> None:
        if self._is_svg:
            return
        filter = create_composite_shadow_filter(style.text_shadows.get())
        if not filter:
            return
        paint.setImageFilter(filter)

    def _render_text_blob(
        self,
        canvas: skia.Canvas,
        blob: skia.TextBlob,
        x: float,
        y: float,
        fill_paint: skia.Paint,
        style: Style,
        bounds: skia.Rect,
        stroke_bounds: skia.Rect,
    ) -> None:
        outline = style.text_stroke.get()
        if not outline:
            canvas.drawTextBlob(blob, x, y, fill_paint)
            return

        mode = outline.mode
        if mode == StrokeMode.CENTER:
            stroke_paint = self._create_stroke_paint(outline.width, outline.color, stroke_bounds)
            canvas.drawTextBlob(blob, x, y, fill_paint)
            canvas.drawTextBlob(blob, x, y, stroke_paint)

        elif mode == StrokeMode.OUTLINE:
            stroke_paint = self._create_stroke_paint(outline.width * 2, outline.color, stroke_bounds)
            canvas.drawTextBlob(blob, x, y, stroke_paint)
            canvas.drawTextBlob(blob, x, y, fill_paint)

        elif mode == StrokeMode.INLINE:
            stroke_paint = self._create_stroke_paint(outline.width, outline.color, stroke_bounds)
            stroke_paint.setBlendMode(skia.BlendMode.kSrcIn)
            canvas.saveLayer(None, None)
            canvas.drawTextBlob(blob, x, y, fill_paint)
            canvas.drawTextBlob(blob, x, y, stroke_paint)
            canvas.restore()

    def _create_stroke_paint(self, width: float, color: PaintSource, bounds: skia.Rect) -> skia.Paint:
        paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width)
        color.apply_to_paint(paint, bounds)
        return paint
