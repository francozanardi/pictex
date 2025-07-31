from typing import Optional
import skia
from .node import Node
from ..models import TextDecoration, Style, RenderProps, Line
from ..text import FontManager, TextShaper
from ..painters import Painter, BackgroundPainter, TextPainter, DecorationPainter, BorderPainter
from .. import utils

class TextNode(Node):

    def __init__(self, style: Style, text: str):
        super().__init__(style)
        self._text = text
        self._text_bounds: Optional[skia.Rect] = None
        self._font_manager: Optional[FontManager] = None
        self._text_shaper: Optional[TextShaper] = None
        self._shaped_lines: Optional[list[Line]] = None

    @property
    def text(self) -> str:
        return self._text

    @property
    def text_bounds(self) -> Optional[skia.Rect]:
        if self._text_bounds is None:
            self._text_bounds = self._compute_text_bounds()
        return self._text_bounds

    @property
    def shaped_lines(self) -> list[Line]:
        if self._shaped_lines is None:
            self._shaped_lines = self._text_shaper.shape(self._text)
        return self._shaped_lines

    def _init_render_dependencies(self, render_props: RenderProps):
        super()._init_render_dependencies(render_props)
        self._font_manager = FontManager(self.computed_styles, self._render_props.font_smoothing)
        self._text_shaper = TextShaper(self.computed_styles, self._font_manager)

    def clear(self):
        super().clear()
        self._text_bounds = None
        self._font_manager = None
        self._text_shaper = None
        self._shaped_lines = None

    def _get_painters(self) -> list[Painter]:
        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
            TextPainter(self.computed_styles, self._font_manager, self.text_bounds, self.content_bounds, self.shaped_lines, self._render_props.is_svg),
            DecorationPainter(self.computed_styles, self._font_manager, self.text_bounds, self.shaped_lines),
        ]

    # We are including the decorations as part of the TextNode content.
    #  However, we could include them only in paint bounds, remove them from here.
    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        line_gap = self.computed_styles.line_height.get() * self.computed_styles.font_size.get()
        current_y = 0
        content_bounds = skia.Rect.MakeEmpty()
        primary_font = self._font_manager.get_primary_font()
        font_metrics = primary_font.getMetrics()

        for line in self.shaped_lines:
            line_bounds = skia.Rect.MakeLTRB(line.bounds.left(), line.bounds.top(), line.bounds.right(), line.bounds.bottom())
            line_bounds.offset(0, current_y)

            self._add_decoration_bounds(content_bounds, self.computed_styles.underline.get(), line_bounds, current_y + font_metrics.fUnderlinePosition)
            self._add_decoration_bounds(content_bounds, self.computed_styles.strikethrough.get(), line_bounds, current_y + font_metrics.fStrikeoutPosition)

            current_y += line_gap

        content_bounds.join(self.text_bounds)
        return content_bounds

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
        paint_bounds = utils.clone_skia_rect(self.margin_bounds)
        paint_bounds.join(self.content_bounds)
        paint_bounds.join(self._compute_shadow_bounds(self.text_bounds, self.computed_styles.text_shadows.get()))
        paint_bounds.join(self._compute_shadow_bounds(self.border_bounds, self.computed_styles.box_shadows.get()))
        return utils.to_int_skia_rect(paint_bounds)

    def _compute_text_bounds(self) -> skia.Rect:
        line_gap = self.computed_styles.line_height.get() * self.computed_styles.font_size.get()
        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()

        for line in self.shaped_lines:
            line_bounds = line.bounds.makeOffset(0, current_y)
            text_bounds.join(line_bounds)
            current_y += line_gap

        return text_bounds

    def _get_all_bounds(self) -> list[skia.Rect]:
        return super()._get_all_bounds() + [self.text_bounds]
