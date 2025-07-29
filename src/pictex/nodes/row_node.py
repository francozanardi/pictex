from typing import Tuple
from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style, VerticalAlignment, HorizontalDistribution
import skia

class RowNode(Node):

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)
        self.clear()

    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        content_bounds = skia.Rect.MakeEmpty()

        for child in self.children:
            if child.computed_styles.position.get() is not None:
                continue

            child_bounds_shifted = child.layout_bounds.makeOffset(content_bounds.width(), 0)
            content_bounds.join(child_bounds_shifted)

        return content_bounds

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

        alignment = self.computed_styles.vertical_alignment.get()
        user_gap = self.computed_styles.gap.get()
        visible_children = [child for child in self.children if child.computed_styles.position.get() is None]
        distribution_gap, start_x = self._distribute_horizontally(user_gap, visible_children)

        final_gap = user_gap + distribution_gap
        current_x = start_x
        for child in visible_children:
            child_height = child.layout_bounds.height()
            container_height = self.content_bounds.height()
            child_y = self.content_bounds.top()

            if alignment == VerticalAlignment.CENTER:
                child_y += (container_height - child_height) / 2
            elif alignment == VerticalAlignment.BOTTOM:
                child_y += container_height - child_height

            child._set_absolute_position(x + current_x, y + child_y)
            current_x += child.layout_bounds.width() + final_gap

    def _distribute_horizontally(self, user_gap: float, visible_children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.horizontal_distribution.get()
        container_width = self.content_bounds.width()
        children_total_width = sum(child.layout_bounds.width() for child in visible_children)
        total_gap_space = user_gap * (len(visible_children) - 1)
        extra_space = container_width - children_total_width - total_gap_space

        start_x = self.content_bounds.left()
        distribution_gap = 0
        if distribution == HorizontalDistribution.RIGHT:
            start_x += extra_space
        elif distribution == HorizontalDistribution.CENTER:
            start_x += extra_space / 2
        elif distribution == HorizontalDistribution.SPACE_BETWEEN and len(visible_children) > 1:
            distribution_gap = extra_space / (len(visible_children) - 1)
        elif distribution == HorizontalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(visible_children)
            start_x += distribution_gap / 2
        elif distribution == HorizontalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(visible_children) + 1)
            start_x += distribution_gap

        return distribution_gap, start_x
