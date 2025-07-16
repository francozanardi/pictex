from .painter import Painter
from ..utils import create_composite_shadow_filter
from ..structs import Line
import skia

class BackgroundPainter(Painter):
    def paint(self, canvas: skia.Canvas, lines: list[Line]) -> None:
        bg_paint = skia.Paint(AntiAlias=True)
        self._style.background.color.apply_to_paint(bg_paint, self._metrics.background_rect)

        if not self._is_svg:
            shadow_filter = create_composite_shadow_filter(self._style.box_shadows)
            if shadow_filter:
                bg_paint.setImageFilter(shadow_filter)

        radius = self._style.background.corner_radius
        if radius > 0:
            canvas.drawRoundRect(self._metrics.background_rect, radius, radius, bg_paint)
        else:
            canvas.drawRect(self._metrics.background_rect, bg_paint)
