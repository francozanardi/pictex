import skia
from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style
from ..utils import clone_skia_rect

class RowNode(Node):

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)
        self.clear()

    def _compute_content_bounds(self) -> skia.Rect:
        content_bounds = skia.Rect.MakeEmpty()

        for child in self.children:
            if child.computed_styles.position.get() is not None:
                continue

            child_bounds_shifted = child.layout_bounds.makeOffset(content_bounds.width(), 0)
            content_bounds.join(child_bounds_shifted)

        size = self.computed_styles.size.get()
        if not size:
            return content_bounds

        width, height = size.get_final_size(content_bounds.width(), content_bounds.height())
        return skia.Rect.MakeWH(width, height)

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = skia.Rect.MakeEmpty()

        for child in self.children:
            if child.computed_styles.position.get() is not None:
                continue

            child_bounds_shifted = child.paint_bounds.makeOffset(paint_bounds.width(), 0)
            paint_bounds.join(child_bounds_shifted)

        paint_bounds.join(self._compute_shadow_bounds(self.box_bounds, self.computed_styles.box_shadows.get()))
        paint_bounds.join(self.layout_bounds)
        return paint_bounds

    def _get_painters(self) -> list[Painter]:
        return [
            BackgroundPainter(self.computed_styles, self.box_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.box_bounds),
        ]

    def _set_absolute_position(self, x: float, y: float) -> None:
        self._absolute_position = (x, y)
        current_x = x + self.content_bounds.left()
        current_y = y + self.content_bounds.top()

        for child in self.children:
            if child.computed_styles.position.get():
                continue

            child._set_absolute_position(current_x, current_y)
            current_x += child.layout_bounds.width()
