from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple
import skia
from ..models import Style, Shadow, RenderProps, CropMode, Transform
from ..painters import Painter
from ..utils import create_composite_shadow_filter, to_int_skia_rect, clone_skia_rect, cached_property, Cacheable
from ..layout import LayoutResult


class Node(Cacheable):
    """Base class for all pictex nodes.
    
    Nodes form a tree structure where layout is computed by stretchable.
    All bounds are in absolute canvas coordinates after layout is computed.
    """

    def __init__(self, style: Style):
        super().__init__()
        self._raw_style = style
        self._parent: Optional[Node] = None
        self._children: list[Node] = []
        self._render_props: Optional[RenderProps] = None
        self._layout_result: Optional[LayoutResult] = None

    @property
    def parent(self) -> Optional[Node]:
        return self._parent

    @property
    def children(self) -> list[Node]:
        return self._children

    @property
    def layout_result(self) -> Optional[LayoutResult]:
        return self._layout_result

    @property
    def absolute_position(self) -> Tuple[int, int]:
        if self._layout_result is None:
            raise RuntimeError("Layout not computed")
        return (self.border_bounds.x(), self.border_bounds.y())

    @cached_property()
    def computed_styles(self) -> Style:
        return self._compute_styles()
    
    @cached_property(group='bounds')
    def size(self) -> Tuple[int, int]:
        """Size of the border box (width, height)."""
        return (int(self.border_bounds.width()), int(self.border_bounds.height()))

    @cached_property(group='bounds')
    def content_bounds(self) -> skia.Rect:
        """Content area bounds in absolute canvas coordinates."""
        if self._layout_result is None:
            raise RuntimeError("Layout not computed")
        return self._layout_result.get_content_bounds()

    @cached_property(group='bounds')
    def padding_bounds(self) -> skia.Rect:
        """Padding box bounds in absolute canvas coordinates."""
        if self._layout_result is None:
            raise RuntimeError("Layout not computed")
        return self._layout_result.get_padding_bounds()

    @cached_property(group='bounds')
    def border_bounds(self) -> skia.Rect:
        """Border box bounds in absolute canvas coordinates."""
        if self._layout_result is None:
            raise RuntimeError("Layout not computed")
        return self._layout_result.get_border_bounds()

    @cached_property(group='bounds')
    def margin_bounds(self) -> skia.Rect:
        """Margin box bounds in absolute canvas coordinates."""
        if self._layout_result is None:
            raise RuntimeError("Layout not computed")
        return self._layout_result.get_margin_bounds()

    @cached_property(group='bounds')
    def paint_bounds(self) -> skia.Rect:
        """Total paint area including shadows, in absolute canvas coordinates."""
        return to_int_skia_rect(self._compute_paint_bounds())

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = clone_skia_rect(self.margin_bounds)
        for child in self.children:
            paint_bounds.join(child.paint_bounds)
        
        paint_bounds.join(
            self._compute_shadow_bounds(self.border_bounds, self.computed_styles.box_shadows.get())
        )

        # This only makes sense if the padding is negative
        paint_bounds.join(self.content_bounds) 

        return paint_bounds

    def _compute_shadow_bounds(self, source_bounds: skia.Rect, shadows: list[Shadow]) -> skia.Rect:
        """Compute bounds expanded by shadow effects."""
        # I don't like this. It only makes sense because it is only being used by paint bounds calculation
        #  However, that responsibility is not clear by the method name.
        #  I mean, if you want to get the shadow bounds in another scenario, this "if" statement don't make any sense.
        if self._render_props and self._render_props.crop_mode == CropMode.CONTENT_BOX:
            return source_bounds
        filter = create_composite_shadow_filter(shadows)
        if filter:
            return filter.computeFastBounds(source_bounds)
        return source_bounds

    def _get_painters(self) -> list[Painter]:
        """Return list of painters for this node. Must be implemented by subclasses."""
        raise NotImplementedError("_get_painters() is not implemented")
    
    def compute_intrinsic_width(self) -> int:
        """Compute intrinsic content width. Used by measure functions."""
        raise NotImplementedError("compute_intrinsic_width() is not implemented")
    
    def compute_intrinsic_height(self) -> int:
        """Compute intrinsic content height. Used by measure functions."""
        raise NotImplementedError("compute_intrinsic_height() is not implemented")

    def paint(self, canvas: skia.Canvas) -> None:
        """Paint this node and its children to the canvas. All bounds are in absolute canvas coordinates."""
        for painter in self._get_painters():
            painter.paint(canvas)
        
        for child in self._children:
            child.paint(canvas)

    def init_render_dependencies(self, render_props: RenderProps) -> None:
        """Initialize rendering dependencies (fonts, text shapers, etc.)."""
        self._render_props = render_props
        for child in self._children:
            child.init_render_dependencies(render_props)

    def set_layout_result(self, layout_result: LayoutResult) -> None:
        """Set the layout result after layout computation"""
        self._layout_result = layout_result
        self._clear_bounds()

    def clear(self) -> None:
        """Clear all cached data and render state."""
        for child in self._children:
            child.clear()
        self._render_props = None
        self._layout_result = None
        self.clear_cache()

    def _clear_bounds(self) -> None:
        """Clear only bounds-related cache."""
        for child in self._children:
            child._clear_bounds()
        self.clear_cache('bounds')

    def _compute_styles(self) -> Style:
        """Compute styles with inheritance from parent."""
        parent_computed_styles = self._parent.computed_styles if self._parent else None
        computed_styles = deepcopy(self._raw_style)
        if not parent_computed_styles:
            return computed_styles

        computed_styles.inherit_from(parent_computed_styles)

        # CSS compliance: resolve text_align based on direction if not set
        if computed_styles.text_align.get() is None:
            from ..models import TextDirection, TextAlign
            direction = computed_styles.direction.get()
            if direction == TextDirection.RTL:
                computed_styles.text_align.set(TextAlign.RIGHT)
                computed_styles.text_align._was_set = False # Don't mark as explicit
            else:
                computed_styles.text_align.set(TextAlign.LEFT)
                computed_styles.text_align._was_set = False # Don't mark as explicit

        return computed_styles

    def _set_children(self, nodes: list[Node]) -> None:
        """Set children and establish parent relationships."""
        for node in nodes:
            node._parent = self
        self._children = nodes
