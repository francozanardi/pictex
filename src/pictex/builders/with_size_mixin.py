from typing import Union, Optional, Literal, TypeAlias
from ..models import Style, Size, SizeValue, SizeValueMode

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

AutomaticSizeType: TypeAlias = Literal['fit-content', 'fit-background-image']

class WithSizeMixin:
    _style: Style

    def _parse_size_value(self, value: Optional[Union[float, int, str]]) -> SizeValue:
        if isinstance(value, (int, float)):
            return SizeValue(SizeValueMode('absolute'), float(value))

        if not isinstance(value, str):
            raise TypeError(f"Unsupported type for size: '{value}' ({type(value).__name__}). "
                            "Expected float, int, or 'number%'.")

        if value.endswith('%'):
            return SizeValue(SizeValueMode('percent'), float(value.rstrip('%')))

        return SizeValue(SizeValueMode(value))

    def size(
            self,
            width: Union[float, int, AutomaticSizeType] = "fit-content",
            height: Union[float, int, AutomaticSizeType] = "fit-content",
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

        - **Automatic**: The dimension is automatically adjusted the
          based on the size of its internal content ("fit-content") or based on the background image size ("fit-background-image").
            `size(width="fit-content", height="fit-background-image")`

        These modes can be mixed, for example: `size(width=100, height="fit-content")`.

        Args:
            width (Optional[Union[float, int, str]]): The horizontal size value.
                Can be an absolute pixel value, a percentage string, or specific mode (e.g. 'fit-content').
            height (Optional[Union[float, int, str]]): The vertical size value.
                Can be an absolute pixel value, a percentage string, or specific mode (e.g. 'fit-content').

        Returns:
            Self: The instance for chaining.

        Raises:
            TypeError: If width or height are of an unsupported type or value.
        """

        parsed_width = self._parse_size_value(width)
        parsed_height = self._parse_size_value(height)

        self._style.size.set(Size(width=parsed_width, height=parsed_height))
        return self

    def fit_background_image(self):
        """Adjusts the element's size to match its background image dimensions.

        This is a convenience method that sets the element's width and height
        to fit the natural size of the background image. It is a shortcut for
        calling `size(width='fit-background-image', height='fit-background-image')`.

        This is particularly useful for ensuring an element, like a Row or Column,
        perfectly contains its background image without distortion or cropping,
        allowing other content to be layered on top.

        The behavior can be overridden by a subsequent call to `.size()`.

        Example:
            ```python
            # A Row that automatically sizes itself to the 'background.png'
            # before rendering text on top of it.
            Row()
                .background_image("path/to/background.png")
                .fit_background_image()
                .render(Text("Text over the full image").position("center", "center"))
            ```

        Returns:
            Self: The instance for method chaining.
        """

        return self.size("fit-background-image", "fit-background-image")
