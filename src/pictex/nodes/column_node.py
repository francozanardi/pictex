from typing import Tuple, Callable
from .node import Node
from .container_node import ContainerNode
from ..models import HorizontalAlignment, VerticalDistribution, SizeValueMode
from ..utils import cached_property
import skia

class ColumnNode(ContainerNode):

    @cached_property(group='bounds')
    def content_width(self) -> int:
        width = super().content_width
        alignment = self.computed_styles.horizontal_alignment.get()
        
        if alignment == HorizontalAlignment.STRETCH:
            children = self._get_positionable_children()
            for child in children:
                child_width = child.computed_styles.width.get()
                if child_width and child_width.mode != SizeValueMode.AUTO:
                    continue
                
                child.clear_bounds()
                child._set_forced_size(width=width)
                child._calculate_bounds()

        return width

    def compute_intrinsic_width(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        return max(child.margin_bounds.width() for child in children)
    
    def compute_intrinsic_height(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1)
        total_children_height = sum(child.margin_bounds.height() for child in children)
        return total_children_height + total_gap

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        positions = []
        user_gap = self.computed_styles.gap.get()
        alignment = self.computed_styles.horizontal_alignment.get()
        start_y, distribution_gap = self._distribute_vertically(user_gap, children)

        final_gap = user_gap + distribution_gap
        current_y = start_y
        for child in children:
            child_bounds = get_child_bounds(child)
            child_width = child_bounds.width()
            container_width = self.content_bounds.width()
            child_x = self.content_bounds.left()

            if alignment == HorizontalAlignment.CENTER:
                child_x += (container_width - child_width) / 2
            elif alignment == HorizontalAlignment.RIGHT:
                child_x += container_width - child_width

            positions.append((child_x, current_y))
            current_y += child_bounds.height() + final_gap

        return positions

    def _distribute_vertically(self, user_gap: float, children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.vertical_distribution.get()
        container_height = self.content_bounds.height()
        children_total_height = sum(child.margin_bounds.height() for child in children)
        total_gap_space = user_gap * (len(children) - 1)
        extra_space = container_height - children_total_height - total_gap_space

        start_y = self.content_bounds.top()
        distribution_gap = 0
        if distribution == VerticalDistribution.BOTTOM:
            start_y += extra_space
        elif distribution == VerticalDistribution.CENTER:
            start_y += extra_space / 2
        elif distribution == VerticalDistribution.SPACE_BETWEEN and len(children) > 1:
            distribution_gap = extra_space / (len(children) - 1)
        elif distribution == VerticalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(children)
            start_y += distribution_gap / 2
        elif distribution == VerticalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(children) + 1)
            start_y += distribution_gap

        return start_y, distribution_gap
