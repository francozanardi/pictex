from typing import Tuple, Callable
from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style
import skia

class ContainerNode(Node):

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)
        self.clear()

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        raise NotImplemented
    
    def _resize_children_if_needed(self, children: list[Node]):
        raise NotImplemented

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = skia.Rect.MakeEmpty()

        children = self._get_positionable_children()
        positions = self._calculate_children_relative_positions(children, lambda node: node.paint_bounds)
        for i, child in enumerate(children):
            position = positions[i]
            child_bounds_shifted = child.paint_bounds.makeOffset(position[0], position[1])
            paint_bounds.join(child_bounds_shifted)

        paint_bounds.join(self._compute_shadow_bounds(self.border_bounds, self.computed_styles.box_shadows.get()))
        paint_bounds.join(self.margin_bounds)
        return paint_bounds

    def _get_painters(self) -> list[Painter]:
        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
        ]

    def _setup_absolute_position(self, x: float = 0, y: float = 0) -> None:
        super()._setup_absolute_position(x, y)
        x, y = self._absolute_position
        positionable_children = self._get_positionable_children()
        self._resize_children_if_needed(positionable_children)
        positions = self._calculate_children_relative_positions(positionable_children, lambda node: node.margin_bounds)
        for i, child in enumerate(positionable_children):
            position = positions[i]
            child._setup_absolute_position(x + position[0], y + position[1])

        non_positionable_children = self._get_non_positionable_children()
        for child in non_positionable_children:
            child._setup_absolute_position()
