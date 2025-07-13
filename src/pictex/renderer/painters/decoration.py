from .painter import Painter
from ..structs import Line
from ..utils import decoration_line_to_line_y_offset, get_line_x_position
import skia

class DecorationPainter(Painter):

    def paint(self, canvas: skia.Canvas, lines: list[Line]) -> None:
        if not self._style.decorations:
            return
        
        primary_font = self._font_manager.get_primary_font()
        font_metrics = primary_font.getMetrics()
        line_gap = self._style.font.line_height * self._style.font.size
        current_y = 0
        block_width = self._metrics.text_rect.width()
        
        for line in lines:
            if not line.runs:
                current_y += line_gap
                continue

            line_x_start = get_line_x_position(line.width, block_width, self._style.alignment)
            
            for deco in self._style.decorations:                
                line_y_offset = decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                
                paint = skia.Paint(AntiAlias=True, StrokeWidth=deco.thickness)
                half_thickness = deco.thickness / 2
                if deco.color:
                    color = deco.color
                    bounds = skia.Rect.MakeLTRB(
                        line_x_start,
                        line_y - half_thickness,
                        line_x_start + line.width,
                        line_y + half_thickness
                    )
                    color.apply_to_paint(paint, bounds)
                else:
                    color = self._style.color
                    color.apply_to_paint(paint, self._metrics.text_rect)

                canvas.drawLine(line_x_start, line_y, line_x_start + line.width, line_y, paint)

            current_y += line_gap
