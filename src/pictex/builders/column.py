from .container import Container
from ..nodes import Node, ColumnNode

class Column(Container):
    """A layout builder that arranges its children vertically.

    A `Column` stacks its children one on top of another. It's a fundamental
    container for creating top-to-bottom layouts.

    Example:
        ```python
        from pictex import Column, Text

        # Create a user info block with centered text.
        user_info = Column(
            Text("Alex Doe").font_size(24).font_weight(700),
            Text("Graphic Designer").color("#657786")
        ).gap(5).align_items('center')
        ```
    """

    def _build_node(self, nodes: list[Node]) -> Node:
        return ColumnNode(self._style, nodes)
