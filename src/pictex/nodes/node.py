from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple
import skia
from ..models import Style, Shadow
from ..painters import Painter
from ..utils import create_composite_shadow_filter
from ..models import RenderProps

class Node:

    def __init__(self, style: Style):
        self._raw_style = style
        self._parent: Optional[Node] = None
        self._children: list[Node] = []
        self._computed_styles: Optional[Style] = None
        self._size: Optional[Tuple[int, int]] = None
        self._content_bounds: Optional[skia.Rect] = None
        self._implicit_content_bounds: Optional[skia.Rect] = None
        self._box_bounds: Optional[skia.Rect] = None
        self._paint_bounds: Optional[skia.Rect] = None
        self._render_props: Optional[RenderProps] = None
        self._absolute_position: Optional[Tuple[float, float]] = None

    @property
    def parent(self) -> Node:
        return self._parent

    @property
    def children(self) -> list[Node]:
        return self._children

    @property
    def computed_styles(self) -> Style:
        if self._computed_styles is None:
            self._computed_styles = self._compute_styles()
        return self._computed_styles

    @property
    def size(self) -> Tuple[int, int]:
        if self._size is None:
            self._size = (self.box_bounds.width(), self.box_bounds.height())
        return self._size

    @property
    def absolute_position(self) -> Optional[Tuple[float, float]]:
        position = self.computed_styles.position.get()
        if not position or not self._parent:
            return self._absolute_position

        parent_width, parent_height = self._parent.size
        self_width, self_height = self.size
        return position.get_absolute_position(self_width, self_height, parent_width, parent_height)

    @property
    def box_bounds(self):
        if self._box_bounds is None:
            self._box_bounds = self._compute_box_bounds()
        return self._box_bounds

    @property
    def content_bounds(self) -> skia.Rect:
        if self._content_bounds is None:
            self._content_bounds = self._compute_final_content_bounds()
        return self._content_bounds

    @property
    def implicit_content_bounds(self) -> skia.Rect:
        if self._implicit_content_bounds is None:
            self._implicit_content_bounds = self._compute_implicit_content_bounds()
        return self._implicit_content_bounds

    @property
    def paint_bounds(self) -> skia.Rect:
        if self._paint_bounds is None:
            self._paint_bounds = self._compute_paint_bounds()
        return self._paint_bounds

    def _compute_box_bounds(self) -> skia.Rect:
        """
        Compute the box bounds, relative to the node box size, (0, 0).
        """
        content_bounds = self.content_bounds
        top_pad, right_pad, bottom_pad, left_pad = self.computed_styles.padding.get()
        return skia.Rect.MakeLTRB(
            content_bounds.left() - left_pad,
            content_bounds.top() - top_pad,
            content_bounds.right() + right_pad,
            content_bounds.bottom() + bottom_pad
        )

    def _compute_final_content_bounds(self) -> skia.Rect:
        implicit_content_bounds = self._compute_implicit_content_bounds()
        size = self.computed_styles.size.get()
        if not size:
            return implicit_content_bounds

        parent_bounds = self._parent.box_bounds if self._parent else None
        parent_width = parent_bounds.width() if parent_bounds else None
        parent_height = parent_bounds.height() if parent_bounds else None
        width, height = size.get_final_size(
            implicit_content_bounds.width(),
            implicit_content_bounds.height(),
            parent_width,
            parent_height
        )
        return skia.Rect.MakeWH(width, height)

    def _compute_implicit_content_bounds(self) -> skia.Rect:
        """
        Compute the inner content bounds (implicit), relative to the node box size, (0, 0).
        Implicit means that it ignores the explicit size set from the styles for the node.
        """
        raise NotImplementedError("_compute_implicit_content_bounds() is not implemented")

    def _compute_paint_bounds(self) -> skia.Rect:
        """
        Compute the paint bounds, including anything that will be painted for this node, even outside the box (like shadows).
        The final result is relative to the node box size, (0, 0).
        """
        raise NotImplementedError("_compute_paint_bounds() is not implemented")

    def _get_painters(self) -> list[Painter]:
        raise NotImplementedError("_get_painters() is not implemented")

    def prepare_tree_for_rendering(self, render_props: RenderProps) -> None:
        """
        Prepares the node and its children to be rendered.
        It's meant to be called in the root node.
        """
        self.clear()
        self._init_render_dependencies(render_props)
        self._calculate_bounds()
        self._set_absolute_position(0, 0)

    def _init_render_dependencies(self, render_props: RenderProps) -> None:
        self._render_props = render_props
        for child in self._children:
            child._init_render_dependencies(render_props)

    def _calculate_bounds(self) -> None:
        for child in self._children:
            child._calculate_bounds()

        bounds = self._get_all_bounds()
        offset_x, offset_y = -self.box_bounds.left(), -self.box_bounds.top()
        for bound in bounds:
            bound.offset(offset_x, offset_y)

    def _get_all_bounds(self) -> list[skia.Rect]:
        return [
            self.content_bounds,
            self.box_bounds,
            self.paint_bounds,
        ]

    def _set_absolute_position(self, x: float, y: float) -> None:
        self._absolute_position = (x, y)

    def paint(self, canvas: skia.Canvas) -> None:
        canvas.save()
        x, y = self.absolute_position
        print("self.absolute_position", self.absolute_position)
        canvas.translate(x, y)
        for painter in self._get_painters():
            painter.paint(canvas)

        canvas.restore()

        for child in self._children:
            child.paint(canvas)

    def clear(self):
        for child in self._children:
            child.clear()

        self._computed_styles = None
        self._size = None
        self._content_bounds = None
        self._implicit_content_bounds = None
        self._box_bounds = None
        self._paint_bounds = None
        self._render_props = None
        self._absolute_position = None

    def _compute_styles(self) -> Style:
        parent_computed_styles = self._parent.computed_styles if self._parent else None
        computed_styles = deepcopy(self._raw_style)
        if not parent_computed_styles:
            return computed_styles

        field_names = computed_styles.get_field_names()
        for field_name in field_names:
            if not computed_styles.is_inheritable(field_name):
                continue
            if computed_styles.is_explicit(field_name):
                continue

            parent_field_value = deepcopy(getattr(parent_computed_styles, field_name))
            setattr(computed_styles, field_name, parent_field_value)

        return computed_styles

    def _compute_shadow_bounds(self, source_bounds: skia.Rect, shadows: list[Shadow]) -> skia.Rect:
        box_shadow_filter = create_composite_shadow_filter(shadows)
        if box_shadow_filter:
            return box_shadow_filter.computeFastBounds(source_bounds)
        return source_bounds

    def _set_children(self, nodes: list[Node]):
        for node in nodes:
            node._parent = self
        self._children = nodes
