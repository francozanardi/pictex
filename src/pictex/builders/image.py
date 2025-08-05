from .element import Element
from .with_size_mixin import WithSizeMixin
from ..nodes import Node, RowNode

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Image(Element, WithSizeMixin):
    """A builder for displaying and styling raster images.

    The `Image` builder is the primary way to include images (like JPG or PNG)
    in your composition. By default, it sizes itself to the natural dimensions
    of the image file. You can override this with `.size()` and
    style it like any other element, applying borders, rounded corners, and shadows.

    Example:
        ```python
        from pictex import Image

        # Create a circular avatar from an image file.
        avatar = (
            Image("avatar.jpg")
            .size(100, 100)
            .border_radius('50%')
            .border(3, "white")
        )
        ```
    """

    def __init__(self, path: str):
        super().__init__()
        self._path = path
        self.background_image(self._path)
        self.fit_background_image()
        self._resize_factor = 1.0

    def resize(self, factor: float) -> Self:
        """
        Resizes the image by a multiplier factor.

        A factor of 1.0 maintains the original size. A factor of 1.1 increases
        the size by 10%, and 0.9 decreases it by 10%. This method adjusts
        both width and height while preserving the aspect ratio.

        This provides a more intuitive way to scale an image compared to
        setting an absolute size. A subsequent call to `.size()` will
        override the effect of this method.

        Example:
            ```python
            # Renders an image at half its original size
            Image("path/to/image.png").resize(0.5)

            # Renders an image 50% larger
            Image("path/to/image.png").resize(1.5)
            ```

        Args:
            factor: The multiplier for resizing the image. Must be a
                positive number.

        Returns:
            Self: The instance for method chaining.

        Raises:
            ValueError: If the factor is not a positive number.
        """
        if factor <= 0:
            raise ValueError("Resize factor must be a positive number.")

        self._resize_factor = factor
        return self

    def _to_node(self) -> Node:
        if self._resize_factor != 1.0:
            image = self._style.background_image.get().get_skia_image()
            if not image:
                raise ValueError(f"Unable to load image '{self._path}'")
            width = image.width()
            height = image.height()
            self.size(width * self._resize_factor, height * self._resize_factor)

        return RowNode(self._style, [])
