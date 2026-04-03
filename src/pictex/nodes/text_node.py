from __future__ import annotations
from copy import deepcopy
from typing import Optional, Union
from .base_text_node import BaseTextNode
from .span_node import SpanNode
from ..models import Style, RenderProps, Line
from ..text import FontManager
from ..text.text_shaper import TextShaper, ResolvedSpan
from ..painters import Painter, BackgroundPainter, TextPainter, DecorationPainter, BorderPainter
from ..utils import cached_property


class TextNode(BaseTextNode):
    """Node that renders text content, with optional per-span inline styles."""

    def __init__(self, style: Style, items: tuple[Union[str, SpanNode], ...]):
        super().__init__(style)
        self._items = items
        self._font_manager: Optional[FontManager] = None
        self._text_shaper: Optional[TextShaper] = None

    @property
    def text(self) -> str:
        return "".join(item if isinstance(item, str) else item.text for item in self._items)

    @cached_property('bounds')
    def shaped_lines(self) -> list[Line]:
        if not self._text_shaper:
            raise RuntimeError("TextShaper not initialized - call init_render_dependencies first")
        return self._text_shaper.shape(self._get_text_wrap_width())

    def init_render_dependencies(self, render_props: RenderProps) -> None:
        super().init_render_dependencies(render_props)
        if not self._render_props:
            raise RuntimeError("_render_props not defined")
        self._text_shaper = TextShaper(
            self._resolve_spans(),
            self.computed_styles,
            self._render_props.font_smoothing,
        )
        self._font_manager = FontManager(self.computed_styles, self._render_props.font_smoothing)

    def clear(self) -> None:
        super().clear()
        self._font_manager = None
        self._text_shaper = None
        self._text_wrap_width = None

    def _get_decoration_painters(self) -> list[Painter]:
        if not self._render_props:
            raise RuntimeError("Dependencies not initialized")
        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
        ]

    def _get_content_painters(self) -> list[Painter]:
        if not self._font_manager or not self._render_props:
            raise RuntimeError("Dependencies not initialized")
        return [
            TextPainter(
                self.computed_styles,
                self._font_manager,
                self.absolute_text_bounds,
                self.content_bounds,
                self.shaped_lines,
                self._render_props.is_svg,
            ),
            DecorationPainter(
                self.computed_styles,
                self._font_manager,
                self.absolute_text_bounds,
                self.shaped_lines,
            ),
        ]

    def _resolve_spans(self) -> list[ResolvedSpan]:
        resolved: list[ResolvedSpan] = []
        offset = 0
        for item in self._items:
            if isinstance(item, str):
                span_style = self.computed_styles
                text = item
                explicit_style = None
            else:
                span_style = self._compute_span_style(item.style)
                text = item.text
                explicit_style = item.style
            resolved.append(ResolvedSpan(text=text, computed_style=span_style, start=offset, explicit_style=explicit_style))
            offset += len(text)
        return resolved

    def _compute_span_style(self, span_raw_style: Style) -> Style:
        computed = deepcopy(span_raw_style)
        computed.inherit_from(self.computed_styles)
        return computed
