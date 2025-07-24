from .container import Container
from ..nodes import Node, RowNode

class Row(Container):

    def _build_node(self, nodes: list[Node]) -> Node:
        return RowNode(self._style, nodes)
