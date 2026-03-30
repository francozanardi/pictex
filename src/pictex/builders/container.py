from typing import Union
from .element import Element
from .text import Text
from copy import deepcopy
from ..nodes import Node
from ..models import JustifyContent, AlignItems, FlexWrap

try:
    from typing import Self # type: ignore[attr-defined]
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

    def justify_content(self, mode: Union[JustifyContent, str]) -> Self:
        """
        Sets how children are distributed along the main axis (CSS justify-content).
        
        For Row: controls horizontal distribution.
        For Column: controls vertical distribution.
        
        Args:
            mode: Distribution mode. Can be 'start', 'center', 'end',
                  'space-between', 'space-around', or 'space-evenly'.
        
        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = JustifyContent(mode.lower())
        self._style.justify_content.set(mode)
        return self

    def align_items(self, mode: Union[AlignItems, str]) -> Self:
        """
        Sets how children are aligned along the cross axis (CSS align-items).
        
        For Row: controls vertical alignment.
        For Column: controls horizontal alignment.
        
        Args:
            mode: Alignment mode. Can be 'start', 'center', 'end', or 'stretch'.
        
        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(mode, str):
            mode = AlignItems(mode.lower())
        self._style.align_items.set(mode)
        return self

    def flex_wrap(self, mode: Union[FlexWrap, str]) -> Self:
        """
        Sets whether children should wrap when they overflow (CSS flex-wrap).
        
        Enables multi-line flex containers, essential for responsive grid-like layouts.
        
        Args:
            mode: Wrap mode. Can be 'nowrap' (default), 'wrap', or 'wrap-reverse'.
                  - 'nowrap': All children stay on one line
                  - 'wrap': Children wrap to new lines when needed
                  - 'wrap-reverse': Children wrap in reverse order
        
        Returns:
            The `Self` instance for chaining.
        
        Example:
            ```python
            Row(
                *[Text(f"Item {i}").size(width=100) for i in range(20)]
            ).flex_wrap('wrap').size(width=500)  # Creates a grid
            ```
        """
        if isinstance(mode, str):
            mode = FlexWrap(mode.lower())
        self._style.flex_wrap.set(mode)
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
