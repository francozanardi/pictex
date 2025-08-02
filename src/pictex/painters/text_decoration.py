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
        primary_font = self._font_manager.get_primary_font()
        font_metrics = primary_font.getMetrics()
        line_gap = self._style.line_height.get() * self._style.font_size.get()
        current_y = self._text_bounds.top() - font_metrics.fAscent
        block_width = self._text_bounds.width()
        
        for line in self._lines:
            if not line.runs:
                current_y += line_gap
                continue

            line_x_start = self._text_bounds.x() + get_line_x_position(line.width, block_width, self._style.text_align.get())
            self._draw_decoration(canvas, self._style.underline.get(), line_x_start, current_y + font_metrics.fUnderlinePosition, line.width)
            self._draw_decoration(canvas, self._style.strikethrough.get(), line_x_start, current_y + font_metrics.fStrikeoutPosition, line.width)

            current_y += line_gap

    def _draw_decoration(
            self,
            canvas: skia.Canvas,
            decoration: Optional[TextDecoration],
            line_x_start: float,
            line_y: float,
            line_width: float
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
            color = self._style.color.get()
            color.apply_to_paint(paint, self._text_bounds)

        canvas.drawLine(line_x_start, line_y, line_x_start + line_width, line_y, paint)
