from typing import Union
from .element import Element
from .text import Text
from copy import deepcopy
from ..nodes import Node
from .sizable import SizableMixin

class Container(Element, SizableMixin):

    def __init__(self, *children: Union[Element, str]):
        super().__init__()
        self._children: list[Element] = self._parse_children(*children)

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
