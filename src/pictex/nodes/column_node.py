from typing import Tuple
from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style, HorizontalAlignment, VerticalDistribution
import skia

class ColumnNode(Node):

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)
        self.clear()

    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        visible_children = self._get_visible_children()
        if not visible_children:
            return skia.Rect.MakeEmpty()

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(visible_children) - 1)
        total_children_height = sum(child.layout_bounds.height() for child in visible_children)
        total_intrinsic_height = total_children_height + total_gap
        max_child_width = max(child.layout_bounds.width() for child in visible_children)
        return skia.Rect.MakeWH(max_child_width, total_intrinsic_height)

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = skia.Rect.MakeEmpty()

        for child in self.children:
            if child.computed_styles.position.get() is not None:
                continue

            child_bounds_shifted = child.paint_bounds.makeOffset(0, paint_bounds.height())
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

        user_gap = self.computed_styles.gap.get()
        alignment = self.computed_styles.horizontal_alignment.get()
        visible_children = [child for child in self.children if child.computed_styles.position.get() is None]
        start_y, distribution_gap = self._distribute_vertically(user_gap, visible_children)

        final_gap = user_gap + distribution_gap
        current_y = start_y
        for child in visible_children:
            child_width = child.layout_bounds.width()
            container_width = self.content_bounds.width()
            child_x = self.content_bounds.left()

            if alignment == HorizontalAlignment.CENTER:
                child_x += (container_width - child_width) / 2
            elif alignment == HorizontalAlignment.RIGHT:
                child_x += container_width - child_width

            child._set_absolute_position(x + child_x, y + current_y)
            current_y += child.layout_bounds.height() + final_gap

    def _distribute_vertically(self, user_gap: float, visible_children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.vertical_distribution.get()
        container_height = self.content_bounds.height()
        children_total_height = sum(child.layout_bounds.height() for child in visible_children)
        total_gap_space = user_gap * (len(visible_children) - 1)
        extra_space = container_height - children_total_height - total_gap_space

        start_y = self.content_bounds.top()
        distribution_gap = 0
        if distribution == VerticalDistribution.BOTTOM:
            start_y += extra_space
        elif distribution == VerticalDistribution.CENTER:
            start_y += extra_space / 2
        elif distribution == VerticalDistribution.SPACE_BETWEEN and len(visible_children) > 1:
            distribution_gap = extra_space / (len(visible_children) - 1)
        elif distribution == VerticalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(visible_children)
            start_y += distribution_gap / 2
        elif distribution == VerticalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(visible_children) + 1)
            start_y += distribution_gap

        return start_y, distribution_gap
