import skia
from .painter import Painter
from ..utils import create_composite_shadow_filter
from ..models import Style

class BackgroundPainter(Painter):

    def __init__(self, style: Style, box_bounds: skia.Rect, is_svg: bool):
        super().__init__(style)
        self._box_bounds = box_bounds
        self._is_svg = is_svg

    def paint(self, canvas: skia.Canvas) -> None:
        bg_paint = skia.Paint(AntiAlias=True)
        self._style.background_color.apply_to_paint(bg_paint, self._box_bounds)

        if not self._is_svg:
            shadow_filter = create_composite_shadow_filter(self._style.box_shadows)
            if shadow_filter:
                bg_paint.setImageFilter(shadow_filter)

        radius = self._style.box_radius
        if radius > 0:
            canvas.drawRoundRect(self._box_bounds, radius, radius, bg_paint)
        else:
            canvas.drawRect(self._box_bounds, bg_paint)
