from .container import Container
from ..nodes import Node, RowNode

class Row(Container):
    """A layout builder that arranges its children horizontally.

    A `Row` places its children one after another in a left-to-right sequence.
    It's a fundamental container for creating side-by-side layouts.

    Example:
        ```python
        from pictex import Row, Image, Text

        # Create a user banner with an avatar and text aligned vertically.
        user_banner = Row(
            Image("avatar.jpg").size(60, 60).border_radius('50%'),
            Text("Username").font_size(24)
        ).gap(15).align_items('center')
        ```
    """

    def _build_node(self, nodes: list[Node]) -> Node:
        return RowNode(self._style, nodes)
