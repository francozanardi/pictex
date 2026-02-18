from typing import Union, Optional, Literal
from ..models import Style, SizeValue, SizeValueMode

try:
    from typing import Self # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self

SizeInput = Union[float, int, Literal['auto', 'fit-content', 'fit-background-image']]

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
            width: Optional[SizeInput] = None,
            height: Optional[SizeInput] = None,
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

        - **Absolute (pixels)**: An `int` or `float` value (e.g., `200`) sets a
          fixed size.

        - **Percentage**: A `str` ending with `%` (e.g., `"50%"`) sets the size
          relative to the parent container's content area.
        
        **Note**: To make an element flexible and fill available space, use 
        `.flex_grow(1)` instead of setting a size mode.

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

    def width(self, value: SizeInput) -> Self:
        """Sets the explicit width of the element's box.

        This is a convenience method that is equivalent to calling `size(width=value)`.

        Args:
            value: The horizontal size value. See `size()` for supported formats.

        Returns:
            Self: The instance for method chaining.
        """
        return self.size(width=value)

    def height(self, value: SizeInput) -> Self:
        """Sets the explicit height of the element's box.

        This is a convenience method that is equivalent to calling `size(height=value)`.

        Args:
            value: The vertical size value. See `size()` for supported formats.

        Returns:
            Self: The instance for method chaining.
        """
        return self.size(height=value)

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

    def min_width(self, value: Union[float, int, str]) -> Self:
        """Sets the minimum width constraint for the element.

        Ensures the element never shrinks below this width, regardless of
        content or flex shrinking behavior.

        Args:
            value: Minimum width value. Can be:
                - Absolute (pixels): int or float (e.g., 100)
                - Percentage: str ending with '%' (e.g., "50%")

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # Ensure text never collapses below 100px
            Text(username).flex_grow(1).min_width(100)
            ```
        """
        parsed_value = self._parse_size_value(value)
        self._style.min_width.set(parsed_value)
        return self

    def max_width(self, value: Union[float, int, str]) -> Self:
        """Sets the maximum width constraint for the element.

        Ensures the element never grows beyond this width, regardless of
        content or flex growing behavior.

        Args:
            value: Maximum width value. Can be:
                - Absolute (pixels): int or float (e.g., 300)
                - Percentage: str ending with '%' (e.g., "80%")

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # Prevent long names from breaking layout
            Text(product_name).size(width="fit-content").max_width(200)
            ```
        """
        parsed_value = self._parse_size_value(value)
        self._style.max_width.set(parsed_value)
        return self

    def min_height(self, value: Union[float, int, str]) -> Self:
        """Sets the minimum height constraint for the element.

        Ensures the element never shrinks below this height, regardless of
        content or flex shrinking behavior.

        Args:
            value: Minimum height value. Can be:
                - Absolute (pixels): int or float (e.g., 50)
                - Percentage: str ending with '%' (e.g., "30%")

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # Ensure card has minimum height even with little content
            Column(children).min_height(200)
            ```
        """
        parsed_value = self._parse_size_value(value)
        self._style.min_height.set(parsed_value)
        return self

    def max_height(self, value: Union[float, int, str]) -> Self:
        """Sets the maximum height constraint for the element.

        Ensures the element never grows beyond this height, regardless of
        content or flex growing behavior.

        Args:
            value: Maximum height value. Can be:
                - Absolute (pixels): int or float (e.g., 400)
                - Percentage: str ending with '%' (e.g., "90%")

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # Limit description height with overflow
            Text(description).max_height(150)
            ```
        """
        parsed_value = self._parse_size_value(value)
        self._style.max_height.set(parsed_value)
        return self

    def aspect_ratio(self, ratio: Union[float, int, str]) -> Self:
        """Sets the aspect ratio constraint for the element.

        Maintains a specific width-to-height proportion. When one dimension
        is specified (e.g., width), the other is calculated automatically
        to maintain the ratio.

        The aspect ratio is expressed as width/height. Common examples:
        - Square: 1.0 or 1
        - Landscape 16:9: 16/9 ≈ 1.778
        - Portrait 9:16: 9/16 ≈ 0.5625
        - Golden ratio: 1.618

        Args:
            ratio: Width-to-height ratio. Can be:
                - Float or int: Direct ratio value (e.g., 1.5, 16/9)
                - String with division: "16/9", "4/3", "1/1"

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # 16:9 video placeholder - specify width, height auto-calculated
            Element().size(width=400).aspect_ratio(16/9)  # height = 225

            # Square Instagram post
            Element().size(width=300).aspect_ratio(1)  # height = 300

            # Vertical story format
            Element().size(height=600).aspect_ratio(9/16)  # width = 337.5
            ```
        """
        if isinstance(ratio, str):
            # Support "16/9" format
            if '/' in ratio:
                parts = ratio.split('/')
                if len(parts) == 2:
                    try:
                        ratio = float(parts[0]) / float(parts[1])
                    except (ValueError, ZeroDivisionError):
                        raise ValueError(f"Invalid aspect ratio format: '{ratio}'. Expected 'width/height' like '16/9'.")
                else:
                    raise ValueError(f"Invalid aspect ratio format: '{ratio}'. Expected 'width/height' like '16/9'.")
            else:
                try:
                    ratio = float(ratio)
                except ValueError:
                    raise ValueError(f"Invalid aspect ratio: '{ratio}'. Expected a number or 'width/height' format.")
        
        if not isinstance(ratio, (int, float)):
            raise TypeError(f"Aspect ratio must be a number or string, got {type(ratio).__name__}")
        
        if ratio <= 0:
            raise ValueError(f"Aspect ratio must be positive, got {ratio}")
        
        self._style.aspect_ratio.set(float(ratio))
        return self
