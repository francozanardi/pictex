from .container import Container
from ..nodes import Node, ColumnNode

class Column(Container):

    def _build_node(self, nodes: list[Node]) -> Node:
        return ColumnNode(self._style, nodes)
