from .element import Element
from ..nodes import Node, TextNode

class Text(Element):
    """The fundamental builder for creating and styling text.

    This is the primary content builder for displaying strings. A `Text` builder
    can have its own unique styles that override any styles inherited from its
    parent containers, allowing for fine-grained control over typography.

    Example:
        ```python
        from pictex import Row, Text

        # Create a row where each Text element has its own style.
        styled_text = Row(
            Text("Hello, ").font_size(30),
            Text("PicTex!").font_size(30).color("blue").font_weight("bold")
        )
        ```
    """

    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def _to_node(self) -> Node:
        return TextNode(self._style, self._text)
