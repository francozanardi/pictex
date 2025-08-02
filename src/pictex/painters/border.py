from typing import Optional
from .painter import Painter
from ..models import Style, Border, BorderStyle
import skia

class BorderPainter(Painter):

    def __init__(self, style: Style, box_bounds: skia.Rect):
        super().__init__(style)
        self._box_bounds = box_bounds

    def paint(self, canvas: skia.Canvas) -> None:
        border = self._style.border.get()
        if not border or border.width <= 0:
            return

        paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=border.width
        )
        border.color.apply_to_paint(paint, self._box_bounds)

        path_effect = self._create_path_effect(border, paint)
        if path_effect:
            paint.setPathEffect(path_effect)

        box_radius = self._style.border_radius.get()

        # This is a little bit hacky: first the inset is because Skia draws the half of the stroke inside and the other half outside.
        #  So, we use inset with the half of the width to draw the border stroke over a smaller rect, achieving a final border inside the box.
        #  Then, we noticed some pixels between the borderline and the edge of the box background.
        #  For that reason, we made an outset with 0.5. This is not perfect, probably some border pixels are drawn outside the final box.
        inset = border.width / 2
        stroke_bounds = self._box_bounds.makeInset(inset, inset)
        rrect = box_radius.apply_corner_radius(stroke_bounds, inset) if box_radius else skia.RRect.MakeRect(stroke_bounds)
        canvas.drawRRect(rrect, paint)

    def _create_path_effect(self, border: Border, paint: skia.Paint) -> Optional[skia.PathEffect]:
        if border.style == BorderStyle.DASHED:
            dash_length = border.width * 2
            gap_length = border.width * 1.5
            return skia.DashPathEffect.Make([dash_length, gap_length], 0)

        if border.style == BorderStyle.DOTTED:
            paint.setStrokeCap(skia.Paint.kRound_Cap)
            return skia.DashPathEffect.Make([0, border.width * 2], 0)

        return None
