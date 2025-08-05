from typing import Union
from .container import Container
from ..nodes import Node, RowNode
from ..models import HorizontalDistribution, VerticalAlignment

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

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
        ).gap(15).vertical_align('center')
        ```
    """

    def _build_node(self, nodes: list[Node]) -> Node:
        return RowNode(self._style, nodes)

    def horizontal_distribution(self, mode: Union[HorizontalDistribution, str]) -> Self:
        """
        Sets how children are distributed along the horizontal axis,
        especially when there is extra space.

        Args:
            mode: Distribution mode. Can be 'left', 'center', 'right',
                  'space-between', 'space-around', or 'space-evenly'.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = HorizontalDistribution(mode.lower())
        self._style.horizontal_distribution.set(mode)
        return self

    def vertical_align(self, mode: Union[VerticalAlignment, str]) -> Self:
        """
        Sets how children are aligned along the vertical axis within the row.

        Args:
            mode: Alignment mode. Can be 'top', 'center', 'bottom', or 'stretch'.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = VerticalAlignment(mode.lower())
        self._style.vertical_alignment.set(mode)
        return self
