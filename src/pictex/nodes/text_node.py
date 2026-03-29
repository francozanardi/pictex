from typing import Optional
import skia
from .node import Node
from ..models import TextDecoration, Style, RenderProps, Line, StrokeMode
from ..text import FontManager, TextShaper
from ..painters import Painter, BackgroundPainter, TextPainter, DecorationPainter, BorderPainter
from ..utils import cached_property, cached_method, to_int_skia_rect


class TextNode(Node):
    """Node that renders text content."""

    def __init__(self, style: Style, text: str):
        super().__init__(style)
        self._text = text
        self._font_manager: Optional[FontManager] = None
        self._text_shaper: Optional[TextShaper] = None
        self._text_wrap_width: Optional[int] = None  # Set by stretchable engine

    @property
    def text(self) -> str:
        return self._text

    @cached_property('bounds')
    def relative_text_bounds(self) -> skia.Rect:
        """Text bounds relative to (0,0). Used for measuring intrinsic size."""
        return self._compute_relative_text_bounds()

    @cached_property('bounds')
    def absolute_text_bounds(self) -> skia.Rect:
        """Text bounds in absolute coordinates."""
        return self.relative_text_bounds.makeOffset(
            self.content_bounds.x(), 
            self.content_bounds.y()
        )

    @cached_property('bounds')
    def shaped_lines(self) -> list[Line]:
        """Text shaped into lines for rendering."""
        if not self._text_shaper:
            raise RuntimeError("TextShaper not initialized - call init_render_dependencies first")
        return self._text_shaper.shape(self._text, self._get_text_wrap_width())

    def init_render_dependencies(self, render_props: RenderProps) -> None:
        super().init_render_dependencies(render_props)
        if not self._render_props:
            raise RuntimeError("_render_props not defined")
        self._font_manager = FontManager(self.computed_styles, self._render_props.font_smoothing)
        self._text_shaper = TextShaper(self.computed_styles, self._font_manager)

    def clear(self) -> None:
        super().clear()
        self._font_manager = None
        self._text_shaper = None
        self._text_wrap_width = None

    def _get_painters(self) -> list[Painter]:
        if not self._font_manager or not self._render_props:
            raise RuntimeError("Dependencies not initialized")
        
        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
            TextPainter(
                self.computed_styles, 
                self._font_manager, 
                self.absolute_text_bounds,
                self.content_bounds,
                self.shaped_lines, 
                self._render_props.is_svg
            ),
            DecorationPainter(
                self.computed_styles, 
                self._font_manager, 
                self.absolute_text_bounds,
                self.shaped_lines
            ),
        ]

    @cached_method('bounds')
    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        """Compute content bounds including text decorations. Relative to (0,0)."""
        if not self._font_manager:
            raise RuntimeError("FontManager not initialized")

        content_bounds = skia.Rect.MakeEmpty()
        current_y = self.relative_text_bounds.top()

        for line in self.shaped_lines:
            # This is not correct actually... the X position should be also calculated, doing something similar that the DecorationPainter
            #  However... I think it shouldn't cause any issue
            line_bounds = line.bounds.makeOffset(0, current_y)
            self._add_decoration_bounds(
                content_bounds, 
                self.computed_styles.underline.get(), 
                line_bounds, 
                current_y + line.metrics.underline
            )
            self._add_decoration_bounds(
                content_bounds, 
                self.computed_styles.strikethrough.get(), 
                line_bounds, 
                current_y + line.metrics.strikethrough
            )
            current_y += line.metrics.height

        content_bounds.join(self.relative_text_bounds)

        return to_int_skia_rect(content_bounds)
    
    def compute_intrinsic_width(self) -> int:
        """Intrinsic width for stretchable measure function.

        Uses the maximum of each line's advance width (float64) and visual
        bounds width. The advance width (line.width) ensures consistency with
        the word-wrapping logic, preventing false wrapping at boundary widths.
        The visual bounds width (line.bounds) accounts for glyph overhang
        (e.g. the last glyph extending beyond its advance), preventing clipping.
        """
        from math import ceil
        if not self.shaped_lines:
            return 0
        return ceil(max(
            max(line.width, line.bounds.width()) for line in self.shaped_lines
        ))
    
    def compute_intrinsic_height(self) -> int:
        """Intrinsic height for stretchable measure function."""
        return self._compute_intrinsic_content_bounds().height()

    def _add_decoration_bounds(
        self,
        dest_bounds: skia.Rect,
        decoration: Optional[TextDecoration],
        line_bounds: skia.Rect,
        line_y: float
    ) -> None:
        if not decoration:
            return
        half_thickness = decoration.thickness / 2
        decoration_bounds = skia.Rect.MakeLTRB(
            line_bounds.left(),
            line_y - half_thickness,
            line_bounds.right(),
            line_y + half_thickness
        )
        dest_bounds.join(decoration_bounds)

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = super()._compute_paint_bounds()
        shadow_bounds = self._compute_shadow_bounds(self.absolute_text_bounds, self.computed_styles.text_shadows.get())
        paint_bounds.join(shadow_bounds)
        
        outline = self.computed_styles.text_stroke.get()
        if not outline or outline.mode == StrokeMode.INLINE:
            return paint_bounds
        
        stroke_expansion = outline.width if outline.mode == StrokeMode.OUTLINE else outline.width / 2
        expanded_text_bounds = self.absolute_text_bounds.makeOutset(stroke_expansion, stroke_expansion)
        paint_bounds.join(expanded_text_bounds)
        return paint_bounds

    def _compute_relative_text_bounds(self) -> skia.Rect:
        """Compute bounds of all text lines, relative to (0,0)."""
        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()

        for line in self.shaped_lines:
            line_bounds = line.bounds.makeOffset(0, current_y)
            text_bounds.join(line_bounds)
            current_y += line.metrics.height

        return text_bounds

    def _get_text_wrap_width(self) -> Optional[int]:
        """Get the width for text wrapping."""
        text_wrap_style = self.computed_styles.text_wrap.get()
        if text_wrap_style.value == 'nowrap':
            return None

        return self._text_wrap_width

    def set_text_wrap_width(self, width: Optional[int]) -> None:
        self._text_wrap_width = width