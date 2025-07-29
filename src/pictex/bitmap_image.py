from __future__ import annotations
import skia
import numpy as np
from .models import Box
import os

class BitmapImage:
    """A wrapper around a rendered raster image.

    This class holds the pixel data from a rendered image and provides
    convenient methods to save it to a file or convert it to other common
    formats like NumPy arrays or Pillow (PIL) Images.

    Objects of this class are typically created by calling `Canvas.render()`.

    Example:
        ```python
        # Assuming 'canvas' is a pre-configured Canvas object
        image = canvas.render("Hello World")

        # Save the image to a file
        image.save("output.png")

        # Get a NumPy array for use with OpenCV or other libraries
        import cv2
        cv2_image = image.to_numpy()
        cv2.imshow("Render", cv2_image)
        cv2.waitKey(0)
        ```

    Attributes:
        content_box (Box): The bounding box of the content (text + padding),
            relative to the image's top-left corner.
        width (int): The total width of the image in pixels.
        height (int): The total height of the image in pixels.
        skia_image (skia.Image): The underlying raw `skia.Image` object for
            advanced use cases.
    """

    def __init__(self, skia_image: skia.Image, content_box: Box):
        """Initializes the Image wrapper.

        Note:
            This constructor is intended for internal use by the library,
            typically called from `Canvas.render()`.

        Args:
            skia_image: The underlying `skia.Image` object.
            content_box: The calculated bounding box of the content area.
        """
        self._skia_image = skia_image
        self._content_box = content_box

    @property
    def content_box(self) -> Box:
        """Gets the bounding box of the content area."""
        return self._content_box

    @property
    def width(self) -> int:
        """Gets the width of the image in pixels."""
        return self._skia_image.width()

    @property
    def height(self) -> int:
        """Gets the height of the image in pixels."""
        return self._skia_image.height()

    @property
    def skia_image(self) -> skia.Image:
        """Gets the raw, underlying `skia.Image` object."""
        return self._skia_image

    def to_bytes(self) -> bytes:
        """Returns the raw pixel data as a byte string.

        The format of the byte string is 32-bit BGRA, with 8 bits per
        component.

        Returns:
            A byte string containing the raw pixel data.
        """
        return self._skia_image.tobytes()

    def to_numpy(self, rgba: bool = False) -> np.ndarray:
        """Converts the image to a NumPy array.

        Args:
            rgba: If `True`, returns the array in RGBA channel order.
                  If `False` (default), returns in BGRA order, which is
                  directly compatible with libraries like OpenCV.

        Returns:
            A NumPy array of shape (height, width, 4) representing the image.
        """
        array = np.frombuffer(self.to_bytes(), dtype=np.uint8).reshape(
            (self.height, self.width, 4)
        )
        if rgba:
            # Swap Blue and Red channels to convert BGRA to RGBA
            return array[:, :, [2, 1, 0, 3]]
        return array

    def to_pillow(self) -> "PillowImage":
        """Converts the image to a Pillow (PIL) Image object.

        The returned Pillow Image will be in 'RGBA' mode.

        Returns:
            A `PIL.Image.Image` object.

        Raises:
            ImportError: If the Pillow library is not installed.
        """
        try:
            from PIL import Image as PillowImage
        except ImportError:
            raise ImportError(
                "Pillow is not installed. Please install it with 'pip install Pillow'."
            )

        return PillowImage.fromarray(self.to_numpy(rgba=True), mode='RGBA')

    def save(self, output_path: str, quality: int = 100) -> None:
        """Saves the image to a file.

        The output format is inferred from the file extension. Supported
        formats are PNG, JPEG, and WebP. Defaults to PNG if the extension
        is unknown.

        Args:
            output_path: The path to save the output image (e.g., 'image.png').
            quality: An integer from 0 to 100 indicating image quality. This
                is only used for lossy formats like JPEG and WebP. It is
                ignored for PNG.

        Raises:
            RuntimeError: If Skia fails to encode the image to the specified
                format.
            IOError: If there is an error writing the file to disk.
        """
        ext = os.path.splitext(output_path)[1].lower()
        format_map = {
            ".png": skia.EncodedImageFormat.kPNG,
            ".jpg": skia.EncodedImageFormat.kJPEG,
            ".jpeg": skia.EncodedImageFormat.kJPEG,
            ".webp": skia.EncodedImageFormat.kWEBP,
        }
        # Default to PNG if the format is not recognized
        fmt = format_map.get(ext, skia.EncodedImageFormat.kPNG)

        data = self._skia_image.encodeToData(fmt, quality)
        if data is None:
            raise RuntimeError(f"Failed to encode image to format '{fmt}'")

        with open(output_path, "wb") as f:
            f.write(data.bytes())

    def show(self) -> None:
        """Displays the image using the default Pillow viewer.

        This method is useful for debugging in scripts and interactive
        environments like Jupyter notebooks.

        Raises:
            ImportError: If the Pillow library is not installed.
        """
        self.to_pillow().show()
