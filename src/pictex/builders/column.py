from typing import Union
from .container import Container
from ..models import VerticalDistribution, HorizontalAlignment
from ..nodes import Node, ColumnNode

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Column(Container):

    def _build_node(self, nodes: list[Node]) -> Node:
        return ColumnNode(self._style, nodes)

    def vertical_distribution(self, mode: Union[VerticalDistribution, str]) -> Self:
        """
        Sets how children are distributed along the vertical axis,
        especially when there is extra space.

        Args:
            mode: Distribution mode. Can be 'top', 'center', 'bottom',
                  'space-between', 'space-around', or 'space-evenly'.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = VerticalDistribution(mode.lower())
        self._style.vertical_distribution.set(mode)
        return self

    def horizontal_align(self, mode: Union[HorizontalAlignment, str]) -> Self:
        """
        Sets how children are aligned along the horizontal axis within the column.

        Args:
            mode: Alignment mode. Can be 'left', 'center', 'right', or 'stretch'.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = HorizontalAlignment(mode.lower())
        self._style.horizontal_alignment.set(mode)
        return self
