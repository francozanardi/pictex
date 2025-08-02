from .element import Element
from ..nodes import Node, TextNode

class Text(Element):

    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def _to_node(self) -> Node:
        return TextNode(self._style, self._text)
