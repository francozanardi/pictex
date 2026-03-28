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
        current_y = self._text_bounds.top()
        block_width = self._parent_bounds.width()
        
        for line in self._lines:
            draw_x_start = self._text_bounds.x() + get_line_x_position(line.width, block_width, self._style.text_align.get())
            current_x = draw_x_start
            
            for run in line.runs:
                blob = run.blob if run.blob else skia.TextBlob.MakeFromShapedText(run.text, run.font)
                self._render_text_blob(canvas, blob, current_x, current_y, paint)
                current_x += run.width
            
            current_y += line.metrics.height

    def _render_text_blob(
        self, 
        canvas: skia.Canvas, 
        blob: skia.TextBlob, 
        x: float, 
        y: float, 
        fill_paint: skia.Paint
    ) -> None:
        outline = self._style.text_stroke.get()
        if not outline:
            canvas.drawTextBlob(blob, x, y, fill_paint)
            return
        
        mode = outline.mode
        if mode == StrokeMode.CENTER:
            stroke_paint = self._create_stroke_paint(outline.width, outline.color)
            canvas.drawTextBlob(blob, x, y, fill_paint)
            canvas.drawTextBlob(blob, x, y, stroke_paint)

        elif mode == StrokeMode.OUTLINE:
            stroke_paint = self._create_stroke_paint(outline.width * 2, outline.color)
            canvas.drawTextBlob(blob, x, y, stroke_paint)
            canvas.drawTextBlob(blob, x, y, fill_paint)

        elif mode == StrokeMode.INLINE:
            stroke_paint = self._create_stroke_paint(outline.width, outline.color)
            stroke_paint.setBlendMode(skia.BlendMode.kSrcIn)
            
            canvas.saveLayer(None, None)
            canvas.drawTextBlob(blob, x, y, fill_paint)
            canvas.drawTextBlob(blob, x, y, stroke_paint)
            canvas.restore()

    def _create_stroke_paint(self, width: float, color: PaintSource) -> skia.Paint:
        paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width)
        color.apply_to_paint(paint, self._text_bounds)
        return paint

