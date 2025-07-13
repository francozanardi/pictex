from .painter import Painter
from ..structs import Line
from ..utils import create_composite_shadow_filter, get_line_x_position
from typing import Optional
import skia

class TextPainter(Painter):

    def paint(self, canvas: skia.Canvas, lines: list[Line]) -> None:
        paint = skia.Paint(AntiAlias=True)
        self._style.color.apply_to_paint(paint, self._metrics.text_rect)
        self._add_shadows_to_paint(paint)
        self._draw_text(canvas, lines, paint)

    def _add_shadows_to_paint(self, paint: skia.Paint) -> None:
        filter = create_composite_shadow_filter(self._style.shadows)
        if not filter:
            return
        paint.setImageFilter(filter)

    def _draw_text(self, canvas: skia.Canvas, lines: list[Line], paint: skia.Paint) -> None:
        line_gap = self._style.font.line_height * self._style.font.size
        current_y = 0
        block_width = self._metrics.text_rect.width()
        outline_paint = self._build_outline_paint()
        
        for line in lines:
            draw_x_start = get_line_x_position(line.width, block_width, self._style.alignment)
            current_x = draw_x_start
            
            for run in line.runs:
                if outline_paint:
                    canvas.drawString(run.text, current_x, current_y, run.font, outline_paint)
                canvas.drawString(run.text, current_x, current_y, run.font, paint)
                current_x += run.width
            
            current_y += line_gap

    def _build_outline_paint(self) -> Optional[skia.Paint]:
        if not self._style.outline_stroke:
            return None
        
        paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=self._style.outline_stroke.width
        )
        self._style.outline_stroke.color.apply_to_paint(paint, self._metrics.text_rect)
