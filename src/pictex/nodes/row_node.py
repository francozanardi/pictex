from typing import Tuple, Callable
from .container_node import ContainerNode
from .node import Node
from ..models import VerticalAlignment, HorizontalDistribution
import skia

class RowNode(ContainerNode):

    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        visible_children = self._get_visible_children()
        if not visible_children:
            return skia.Rect.MakeEmpty()

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(visible_children) - 1)
        total_children_width = sum(child.layout_bounds.width() for child in visible_children)
        total_intrinsic_width = total_children_width + total_gap
        max_child_height = max(child.layout_bounds.height() for child in visible_children)
        return skia.Rect.MakeWH(total_intrinsic_width, max_child_height)

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        positions = []
        alignment = self.computed_styles.vertical_alignment.get()
        user_gap = self.computed_styles.gap.get()
        distribution_gap, start_x = self._distribute_horizontally(user_gap, children)

        final_gap = user_gap + distribution_gap
        current_x = start_x
        for child in children:
            child_bounds = get_child_bounds(child)
            child_height = child_bounds.height()
            container_height = self.content_bounds.height()
            child_y = self.content_bounds.top()

            if alignment == VerticalAlignment.CENTER:
                child_y += (container_height - child_height) / 2
            elif alignment == VerticalAlignment.BOTTOM:
                child_y += container_height - child_height

            positions.append((current_x, child_y))
            current_x += child_bounds.width() + final_gap

        return positions

    def _distribute_horizontally(self, user_gap: float, children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.horizontal_distribution.get()
        container_width = self.content_bounds.width()
        children_total_width = sum(child.layout_bounds.width() for child in children)
        total_gap_space = user_gap * (len(children) - 1)
        extra_space = container_width - children_total_width - total_gap_space

        start_x = self.content_bounds.left()
        distribution_gap = 0
        if distribution == HorizontalDistribution.RIGHT:
            start_x += extra_space
        elif distribution == HorizontalDistribution.CENTER:
            start_x += extra_space / 2
        elif distribution == HorizontalDistribution.SPACE_BETWEEN and len(children) > 1:
            distribution_gap = extra_space / (len(children) - 1)
        elif distribution == HorizontalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(children)
            start_x += distribution_gap / 2
        elif distribution == HorizontalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(children) + 1)
            start_x += distribution_gap

        return distribution_gap, start_x
