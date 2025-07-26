from typing import Self, Union, Optional

from ..models import Style, Size, SizeValue

class SizableMixin:
    _style: Style

    def _parse_size_value(self, value: Optional[Union[float, int, str]]) -> SizeValue:
        if value is None:
            return SizeValue(mode='fit-content')

        if isinstance(value, (int, float)):
            return SizeValue(mode='absolute', value=float(value))

        if isinstance(value, str) and value.endswith('%'):
            return SizeValue(mode='percent', value=float(value.rstrip('%')))

        raise TypeError(f"Unsupported type for size: '{value}' ({type(value).__name__}). "
                        "Expected float, int, or 'number%'.")

    def size(
            self,
            width: Optional[Union[float, int, str]] = None,
            height: Optional[Union[float, int, str]] = None
    ) -> Self:
        """Sets the explicit size of the element.

        The width and height can be defined independently. If an argument is
        not provided, its corresponding dimension is not changed. Each dimension
        supports three modes:

        - **Absolute (pixels)**: An `int` or `float` value that sets the
          dimension to a fixed size.
            `size(width=200, height=150)`

        - **Percentage**: A `str` ending with `%` that sets the dimension
          relative to the parent container's size.
            `size(width="50%", height="75%")`

        - **None**: The dimension is automatically adjusted the
          based on the size of its internal content (fit-content mode).
            `size(width="fit-content")`

        These modes can be mixed, for example: `size(width=100, height="fit-content")`.

        Args:
            width (Optional[Union[float, int, str]]): The horizontal size value.
                Can be an absolute pixel value, a percentage string, or `None`.
                If `None`, the width will change depending on the content.
            height (Optional[Union[float, int, str]]): The vertical size value.
                Can be an absolute pixel value, a percentage string, or `None`.
                If `None`, the height will change depending on the content.

        Returns:
            Self: The instance for chaining.

        Raises:
            TypeError: If width or height are of an unsupported type or value.
        """

        parsed_width = self._parse_size_value(width)
        parsed_height = self._parse_size_value(height)

        self._style.size.set(Size(width=parsed_width, height=parsed_height))
        return self
