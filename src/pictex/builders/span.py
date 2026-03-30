from __future__ import annotations
from copy import deepcopy
from typing import TYPE_CHECKING, Optional, Union
from .inline_styleable import InlineStyleable

if TYPE_CHECKING:
    from ..models import Style


class Span(InlineStyleable):
    """An inline text fragment with its own typography styles.

    Used inside ``Text`` to apply styles (color, font weight, etc.) to
    a specific portion of text. Only typography properties have any effect;
    layout properties (padding, margin, border, etc.) are intentionally
    unavailable.

    ``Span`` items can be nested: a child ``Span`` inherits the explicit
    typography styles of its parent and can override them further.

    Example:
        ```python
        Text(
            "Hello ",
            Span("world ", Span("today").font_weight("bold")).color("red"),
            " done",
        )
        ```
    """

    def __init__(self, *items: Union[str, "Span"]):
        super().__init__()
        self._items = items

    @property
    def text(self) -> str:
        return "".join(item if isinstance(item, str) else item.text for item in self._items)

    def _to_span_nodes(self) -> list:
        """Flatten this span into a list of SpanNode objects."""
        return self.__to_span_nodes_recursive(None)

    def __to_span_nodes_recursive(self, parent_raw_style: Optional["Style"]) -> list:
        """Internal recursive traversal for nested Span blocks."""
        from ..nodes.span_node import SpanNode
        composed_style = self.__compose_with_parent(parent_raw_style)
        result = []
        for item in self._items:
            if isinstance(item, str):
                result.append(SpanNode(text=item, style=composed_style))
            else:
                result.extend(item.__to_span_nodes_recursive(composed_style))
        return result

    def __compose_with_parent(self, parent_raw_style: Optional["Style"]) -> "Style":
        """Return this span's raw style with explicit parent fields inherited in."""
        if parent_raw_style is None:
            return self._style
        composed = deepcopy(self._style)
        composed.inherit_from(parent_raw_style, only_explicit=True)
        return composed
