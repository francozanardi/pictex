from typing import Union
from .element import Element
from .span import Span
from ..nodes import Node, TextNode

class Text(Element):
    """The fundamental builder for creating and styling text.

    Accepts plain strings and inline ``Span`` fragments. When multiple items
    are provided, each ``Span`` can carry its own typography overrides (color,
    weight, etc.) on top of the block-level style.

    Example:
        ```python
        from pictex import Row, Text, Span

        # Plain text
        Text("Hello, PicTex!").font_size(30)

        # Inline styled fragments
        Text(
            "Hello, ",
            Span("PicTex!").color("blue").font_weight("bold"),
        ).font_size(30)
        ```
    """

    def __init__(self, *items: Union[str, Span]):
        super().__init__()
        self._items = items

    def _to_node(self) -> Node:
        flat: list = []
        for item in self._items:
            if isinstance(item, str):
                flat.append(item)
            else:
                flat.extend(item._to_span_nodes())
        return TextNode(self._style, tuple(flat))
