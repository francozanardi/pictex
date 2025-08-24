from typing import Tuple, Callable
from .container_node import ContainerNode
from .node import Node
from ..models import VerticalAlignment, HorizontalDistribution, SizeValueMode
from ..utils import cached_property
import skia

class RowNode(ContainerNode):

    def compute_intrinsic_width(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1)
        total_children_width = sum(child.margin_bounds.width() for child in children)
        return total_children_width + total_gap
    
    def compute_intrinsic_height(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        return max(child.margin_bounds.height() for child in children)
    
    @cached_property(group='bounds')
    def content_height(self) -> int:
        height = super().content_height
        alignment = self.computed_styles.vertical_alignment.get()
        
        if alignment == VerticalAlignment.STRETCH:
            children = self._get_positionable_children()
            for child in children:
                child_height = child.computed_styles.height.get()
                if child_height and child_height.mode != SizeValueMode.AUTO:
                    continue
                
                child.clear_bounds()
                child._set_forced_size(height=height)
                child._calculate_bounds()

        return height

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
        children_total_width = sum(child.margin_bounds.width() for child in children)
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

    def _resize_children_if_needed(self, children: list[Node]):
        fixed_children_width = 0
        flexible_children: list[Node] = []
        user_gap = self.computed_styles.gap.get()

        for child in children:
            child_width_style = child.computed_styles.width.get()
            if child_width_style and child_width_style.mode == SizeValueMode.FILL_AVAILABLE:
                flexible_children.append(child)
            else:
                fixed_children_width += child.size[0]

        container_width = self.content_bounds.width()
        total_gap_space = user_gap * (len(children) - 1) if len(children) > 1 else 0
        remaining_space = container_width - fixed_children_width - total_gap_space
        
        if not flexible_children:
            return
        
        space_per_flexible_child = max(0, remaining_space / len(flexible_children))
        for child in flexible_children:
            child.clear_bounds()
            child._set_forced_size(width=space_per_flexible_child)
            child._calculate_bounds()
