from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple
import skia
from ..models import Style, Shadow, PositionMode, RenderProps, CropMode
from ..painters import Painter
from ..utils import create_composite_shadow_filter, clone_skia_rect, to_int_skia_rect, cached_property, Cacheable
from ..layout import SizeResolver

class Node(Cacheable):

    def __init__(self, style: Style):
        super().__init__()
        self._raw_style = style
        self._parent: Optional[Node] = None
        self._children: list[Node] = []
        self._forced_size: Tuple[Optional[int], Optional[int]] = (None, None)
        self._render_props: Optional[RenderProps] = None
        self._absolute_position: Optional[Tuple[float, float]] = None

    @property
    def parent(self) -> Node:
        return self._parent

    @property
    def children(self) -> list[Node]:
        return self._children

    @cached_property()
    def computed_styles(self) -> Style:
        return self._compute_styles()

    @cached_property(group='bounds')
    def size(self) -> Tuple[int, int]:
        return (self.border_bounds.width(), self.border_bounds.height())
    
    @cached_property(group='bounds')
    def content_width(self) -> int:
        return SizeResolver(self).resolve_width()

    @cached_property(group='bounds')
    def content_height(self) -> int:
        return SizeResolver(self).resolve_height()

    @property
    def absolute_position(self) -> Optional[Tuple[float, float]]:
        if self._absolute_position:
            return self._absolute_position

        position = self.computed_styles.position.get()
        if not position or not self._parent:
            return None

        self_width, self_height = self.size
        if position.mode == PositionMode.RELATIVE:
            parent_content_bounds = self._parent.content_bounds
            parent_position = self._parent.absolute_position
            self_position = position.get_relative_position(self_width, self_height, parent_content_bounds.width(), parent_content_bounds.height())
            self._absolute_position = (
                parent_position[0] + parent_content_bounds.left() + self_position[0],
                parent_position[1] + parent_content_bounds.top() + self_position[1]
            )
            return self._absolute_position

        root = self._get_root()
        root_width, root_height = root.size
        self._absolute_position = position.get_relative_position(self_width, self_height, root_width, root_height)
        return self._absolute_position

    @cached_property(group='bounds')
    def padding_bounds(self):
        return to_int_skia_rect(self._compute_padding_bounds())

    @cached_property(group='bounds')
    def border_bounds(self):
        return to_int_skia_rect(self._compute_border_bounds())

    @cached_property(group='bounds')
    def margin_bounds(self):
        return to_int_skia_rect(self._compute_margin_bounds())

    @cached_property(group='bounds')
    def content_bounds(self) -> skia.Rect:
        return to_int_skia_rect(skia.Rect.MakeWH(self.content_width, self.content_height))

    @cached_property(group='bounds')
    def paint_bounds(self) -> skia.Rect:
        return to_int_skia_rect(self._compute_paint_bounds())

    def _compute_padding_bounds(self) -> skia.Rect:
        """
        Compute the box bounds, relative to the node box size, (0, 0).
        """
        content_bounds = self.content_bounds
        padding = self.computed_styles.padding.get()
        return skia.Rect.MakeLTRB(
            content_bounds.left() - padding.left,
            content_bounds.top() - padding.top,
            content_bounds.right() + padding.right,
            content_bounds.bottom() + padding.bottom
        )

    def _compute_border_bounds(self) -> skia.Rect:
        """
        Compute the box bounds, relative to the node box size, (0, 0).
        """
        padding_bounds = self.padding_bounds
        border = self.computed_styles.border.get()
        if not border:
            return clone_skia_rect(padding_bounds)

        return skia.Rect.MakeLTRB(
            padding_bounds.left() - border.width,
            padding_bounds.top() - border.width,
            padding_bounds.right() + border.width,
            padding_bounds.bottom() + border.width
        )

    def _compute_margin_bounds(self) -> skia.Rect:
        """
        Compute the layout bounds (box + margin), relative to the node box size, (0, 0).
        """
        border_bounds = self.border_bounds
        margin = self.computed_styles.margin.get()
        return skia.Rect.MakeLTRB(
            border_bounds.left() - margin.left,
            border_bounds.top() - margin.top,
            border_bounds.right() + margin.right,
            border_bounds.bottom() + margin.bottom
        )

    def _compute_paint_bounds(self) -> skia.Rect:
        """
        Compute the paint bounds, including anything that will be painted for this node, even outside the box (like shadows).
        The final result is relative to the node box size, (0, 0).
        """
        raise NotImplementedError("_compute_paint_bounds() is not implemented")

    def _get_painters(self) -> list[Painter]:
        raise NotImplementedError("_get_painters() is not implemented")
    
    def compute_intrinsic_width(self) -> skia.Rect:
        """
        Compute the intrinsic width. That is, ignoring any size strategy set.
        It measures the actual content (if the strategy is 'fit-content', then it's the same that self.content_width)
        """
        raise NotImplementedError("compute_intrinsic_width() is not implemented")
    
    def compute_intrinsic_height(self) -> skia.Rect:
        """
        Compute the intrinsic height. That is, ignoring any size strategy set.
        It measures the actual content (if the strategy is 'fit-content', then it's the same that self.content_height)
        """
        raise NotImplementedError("compute_intrinsic_height() is not implemented")

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
        offset_x, offset_y = -self.margin_bounds.left(), -self.margin_bounds.top()
        for bound in bounds:
            bound.offset(offset_x, offset_y)

    def _get_all_bounds(self) -> list[skia.Rect]:
        return [
            self.content_bounds,
            self.padding_bounds,
            self.border_bounds,
            self.margin_bounds,
            self.paint_bounds,
        ]

    def _set_absolute_position(self, x: float, y: float) -> None:
        has_position = self.computed_styles.position.get() is not None
        has_parent = self._parent is not None
        if not has_position or not has_parent:
            self._absolute_position = (x, y)

    def paint(self, canvas: skia.Canvas) -> None:
        canvas.save()
        x, y = self.absolute_position
        canvas.translate(x, y)
        for painter in self._get_painters():
            painter.paint(canvas)

        canvas.restore()

        for child in self._children:
            child.paint(canvas)

    def clear(self):
        for child in self._children:
            child.clear()

        self._render_props = None
        self._absolute_position = None
        self._forced_size = (None, None)
        self.clear_cache()

    def clear_bounds(self):
        """
        Resets only the calculated layout and bounds information.
        This is a more targeted version of clear().
        """
        for child in self._children:
            child.clear()

        self._forced_size = (None, None)
        self.clear_cache('bounds')

    def _set_forced_size(self, width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Allows a parent to impose a size on this node."""
        self._forced_size = (width, height)

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
        # I don't like this. It only makes sense because it is only being used by paint bounds calculation
        #  However, that responsibility is not clear by the method name.
        #  I mean, if you want to get the shadow bounds in another scenario, this "if" statement don't make any sense.
        if self._render_props.crop_mode == CropMode.CONTENT_BOX:
            return source_bounds
        filter = create_composite_shadow_filter(shadows)
        if filter:
            return filter.computeFastBounds(source_bounds)
        return source_bounds

    def _set_children(self, nodes: list[Node]):
        for node in nodes:
            node._parent = self
        self._children = nodes

    def _get_root(self) -> Optional[Node]:
        root = self
        while root._parent:
            root = root._parent
        return root

    def _get_positionable_children(self) -> list[Node]:
        return [child for child in self.children if child.computed_styles.position.get() is None]
