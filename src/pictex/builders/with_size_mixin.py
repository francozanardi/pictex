from typing import Union, Optional, Literal
from ..models import Style, SizeValue, SizeValueMode

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

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
            width: Optional[Union[float, int, Literal['auto', 'fit-content', 'fit-background-image', 'fill-available']]] = None,
            height: Optional[Union[float, int, Literal['auto', 'fit-content', 'fit-background-image', 'fill-available']]] = None,
    ) -> Self:
        """Sets the explicit size of the element's box using the border-box model.

        The width and height are defined independently and control the total
        dimensions of the element, including its padding and border.

        Each dimension supports several modes:

        - **`'auto'`**: The size is context-dependent. It typically
          behaves like `'fit-content'`, but will yield to parent layout
          constraints, such as stretching to fill the space in a `Row` or
          `Column` with align `stretch`. This is the default behavior.

        - **`'fit-content'`**: The size is explicitly set to wrap the element's
          content. This will override parent constraints like `stretch`.

        - **`'fit-background-image'`**: The size is explicitly set to match the
          dimensions of the element's background image.

        - **`'fill-available'`**: The element becomes flexible and will expand or shrink to
          occupy a share of the available space in its parent container.

        - **Absolute (pixels)**: An `int` or `float` value (e.g., `200`) sets a
          fixed size.

        - **Percentage**: A `str` ending with `%` (e.g., `"50%"`) sets the size
          relative to the parent container's content area.

        Args:
            width (Union[float, int, str]): The horizontal size value.
                Defaults to "auto".
            height (Union[float, int, str]): The vertical size value.
                Defaults to "auto".

        Returns:
            Self: The instance for method chaining.
        """

        if width is not None:
            parsed_width = self._parse_size_value(width)
            self._style.width.set(parsed_width)

        if height is not None:
            parsed_height = self._parse_size_value(height)
            self._style.height.set(parsed_height)

        return self

    def fit_background_image(self) -> Self:
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
