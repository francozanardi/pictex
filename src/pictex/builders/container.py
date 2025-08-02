from typing import Union
from .element import Element
from .text import Text
from copy import deepcopy
from ..nodes import Node

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Container(Element):

    def __init__(self, *children: Union[Element, str]):
        super().__init__()
        self._children: list[Element] = self._parse_children(*children)

    def gap(self, value: float) -> Self:
        """
        Sets a fixed space between each child element along the main axis.

        This is often simpler than adding margins to each child individually.

        Args:
            value: The space, in pixels, to add between children.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.gap.set(value)
        return self

    def _to_node(self) -> Node:
        children_nodes = []
        for child in self._children:
            children_nodes.append(child._to_node())
        return self._build_node(children_nodes)

    def _build_node(self, nodes: list[Node]) -> Node:
        raise NotImplementedError()

    def _parse_children(self, *children: Union[Element, str]) -> list[Element]:
        parsed_children = []
        for child in list(children):
            if isinstance(child, str):
                child = Text(child)
            else:
                child = deepcopy(child)
            parsed_children.append(child)

        return parsed_children
