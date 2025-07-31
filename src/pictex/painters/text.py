from .painter import Painter
from ..text import FontManager
from ..utils import create_composite_shadow_filter, get_line_x_position
from typing import Optional
import skia
from ..models import Style, Line

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
        paint = skia.Paint(AntiAlias=True)
        self._style.color.get().apply_to_paint(paint, self._text_bounds)
        self._add_shadows_to_paint(paint)
        self._draw_text(canvas, paint)

    def _add_shadows_to_paint(self, paint: skia.Paint) -> None:
        if self._is_svg:
            return

        filter = create_composite_shadow_filter(self._style.text_shadows.get())
        if not filter:
            return
        paint.setImageFilter(filter)

    def _draw_text(self, canvas: skia.Canvas, paint: skia.Paint) -> None:
        primary_font = self._font_manager.get_primary_font()
        font_metrics = primary_font.getMetrics()
        current_y = self._text_bounds.top() - font_metrics.fAscent
        line_gap = self._style.line_height.get() * self._style.font_size.get()
        block_width = self._parent_bounds.width()
        outline_paint = self._build_outline_paint()
        
        for line in self._lines:
            draw_x_start = self._text_bounds.x() + get_line_x_position(line.width, block_width, self._style.text_align.get())
            current_x = draw_x_start
            
            for run in line.runs:
                if outline_paint:
                    canvas.drawString(run.text, current_x, current_y, run.font, outline_paint)
                canvas.drawString(run.text, current_x, current_y, run.font, paint)
                current_x += run.width
            
            current_y += line_gap

    def _build_outline_paint(self) -> Optional[skia.Paint]:
        outline = self._style.text_stroke.get()
        if not outline:
            return None
        
        paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=outline.width
        )
        outline.color.apply_to_paint(paint, self._text_bounds)
        return paint
