from math import ceil
from typing import Optional
import skia
from .node import Node
from ..models import Line, StrokeMode, TextDecoration, Overflow
from ..utils import cached_property, cached_method, to_int_skia_rect, clone_skia_rect


class BaseTextNode(Node):
    """Abstract base for text-rendering nodes.

    Provides shared logic for wrap width management, bounds computation,
    intrinsic sizing, and paint bounds. Subclasses must implement
    ``shaped_lines``.
    """

    def __init__(self, style):
        super().__init__(style)
        self._text_wrap_width: Optional[int] = None

    @cached_property('bounds')
    def shaped_lines(self) -> list[Line]:
        raise NotImplementedError("Subclasses must implement shaped_lines")

    @cached_property('bounds')
    def relative_text_bounds(self) -> skia.Rect:
        return self._compute_relative_text_bounds()

    @cached_property('bounds')
    def absolute_text_bounds(self) -> skia.Rect:
        return self.relative_text_bounds.makeOffset(
            self.content_bounds.x(),
            self.content_bounds.y(),
        )

    def compute_intrinsic_width(self) -> int:
        """Uses the maximum of each line's advance width and visual bounds width.

        The advance width (line.width) ensures consistency with the
        word-wrapping logic, preventing false wrapping at boundary widths.
        The visual bounds width (line.bounds) accounts for glyph overhang
        (e.g. the last glyph extending beyond its advance), preventing clipping.
        """
        if not self.shaped_lines:
            return 0
        return ceil(max(
            max(line.width, line.bounds.width()) for line in self.shaped_lines
        ))

    def compute_intrinsic_height(self) -> int:
        return self._compute_intrinsic_content_bounds().height()

    def set_text_wrap_width(self, width: Optional[int]) -> None:
        self._text_wrap_width = width

    def _get_text_wrap_width(self) -> Optional[int]:
        if self.computed_styles.text_wrap.get().value == 'nowrap':
            return None
        return self._text_wrap_width

    def _compute_relative_text_bounds(self) -> skia.Rect:
        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()
        for line in self.shaped_lines:
            line_bounds = line.bounds.makeOffset(0, current_y)
            text_bounds.join(line_bounds)
            current_y += line.metrics.height
        return text_bounds

    @cached_method('bounds')
    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        content_bounds = skia.Rect.MakeEmpty()
        current_y = 0
        for line in self.shaped_lines:
            line_bounds = line.bounds.makeOffset(0, current_y)
            for run in line.runs:
                self._add_decoration_bounds(
                    content_bounds, run.style.underline.get(),
                    line_bounds, current_y + line.metrics.underline,
                )
                self._add_decoration_bounds(
                    content_bounds, run.style.strikethrough.get(),
                    line_bounds, current_y + line.metrics.strikethrough,
                )
            current_y += line.metrics.height
        content_bounds.join(self.relative_text_bounds)
        return to_int_skia_rect(content_bounds)

    def _add_decoration_bounds(
        self,
        dest_bounds: skia.Rect,
        decoration: Optional[TextDecoration],
        line_bounds: skia.Rect,
        line_y: float,
    ) -> None:
        if not decoration:
            return
        half_thickness = decoration.thickness / 2
        dest_bounds.join(skia.Rect.MakeLTRB(
            line_bounds.left(),
            line_y - half_thickness,
            line_bounds.right(),
            line_y + half_thickness,
        ))

    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = super()._compute_paint_bounds()
        overflow_visible = self.computed_styles.overflow.get() == Overflow.VISIBLE
        if overflow_visible:
            shadow_bounds = self._compute_shadow_bounds(
                self.absolute_text_bounds, self.computed_styles.text_shadows.get()
            )
            paint_bounds.join(shadow_bounds)

        if not overflow_visible:
            return paint_bounds

        outline = self.computed_styles.text_stroke.get()
        if not outline or outline.mode == StrokeMode.INLINE:
            return paint_bounds

        stroke_expansion = outline.width if outline.mode == StrokeMode.OUTLINE else outline.width / 2
        stroke_bounds = self.absolute_text_bounds.makeOutset(stroke_expansion, stroke_expansion)
        paint_bounds.join(stroke_bounds)
        return paint_bounds
