from __future__ import annotations
import skia
import numpy as np
from .models import Box
import os

class Image:
    """
    A wrapper around a rendered Skia image.

    This class provides convenient methods to access image data, save to a file,
    or convert to other popular formats like NumPy arrays or Pillow images.
    """
    def __init__(self, skia_image: skia.Image, content_box: Box):
        """
        Initializes the Image wrapper. This is typically done by `Canvas.render()`.
        
        Args:
            skia_image: The underlying `skia.Image` object.
            content_box: The calculated bounding box of the content area.
        """
        self._skia_image = skia_image
        self._content_box = content_box

    @property
    def content_box(self) -> Box:
        """
        The bounding box of the content (text + padding), relative to the image's top-left.
        
        Returns:
            A `Box` object with x, y, width, and height attributes.
        """
        return self._content_box

    @property
    def width(self) -> int:
        """The width of the image in pixels."""
        return self._skia_image.width()

    @property
    def height(self) -> int:
        """The height of the image in pixels."""
        return self._skia_image.height()

    @property
    def skia_image(self) -> skia.Image:
        """
        Returns the raw, underlying skia.Image object for advanced use cases.
        """
        return self._skia_image

    def to_bytes(self) -> bytes:
        """
        Returns the pixel data as a raw byte string in BGRA format.
        """
        return self._skia_image.tobytes()

    def to_numpy(self, rgba: bool = False) -> np.ndarray:
        """
        Converts the image to a NumPy array.

        Args:
            rgba: If True, returns the array in RGBA channel order.
                  If False (default), returns in BGRA order, which is
                  directly compatible with libraries like OpenCV.

        Returns:
            A NumPy array representing the image.
        """
        array = np.frombuffer(self.to_bytes(), dtype=np.uint8).reshape(
            (self.height, self.width, 4)
        )
        if rgba:
            # Swap Blue and Red channels for RGBA
            return array[:, :, [2, 1, 0, 3]]
        return array

    def to_pillow(self):
        """
        Converts the image to a Pillow (PIL) Image object.
        Requires Pillow to be installed (`pip install Pillow`).
        """
        try:
            from PIL import Image as PillowImage
        except ImportError:
            raise ImportError("Pillow is not installed. Please install it with 'pip install Pillow'.")
        
        # Pillow works with RGBA arrays
        return PillowImage.fromarray(self.to_numpy(rgba=True))

    def save(self, output_path: str, quality: int = 100) -> None:
        """
        Saves the image to a file. The format is inferred from the extension.
        
        Args:
            output_path: The path to save the output image (e.g., 'image.png').
            quality: An integer from 0 to 100 indicating image quality. Used for lossy formats
                     like JPEG and WebP. Ignored for PNG.
        """
        ext = os.path.splitext(output_path)[1].lower()
        format_map = {
            ".png": skia.EncodedImageFormat.kPNG,
            ".jpg": skia.EncodedImageFormat.kJPEG,
            ".jpeg": skia.EncodedImageFormat.kJPEG,
            ".webp": skia.EncodedImageFormat.kWEBP,
        }
        if ext not in format_map:
            ext = ".png"
        fmt = format_map[ext]
        data = self._skia_image.encodeToData(fmt, quality)
        if data is None:
            raise RuntimeError(f"Failed to encode image to format '{fmt}'")
        
        with open(output_path, "wb") as f:
            f.write(data.bytes())
        
    def show(self) -> None:
        """
        Displays the image using Pillow. Useful for debugging in scripts.
        Requires Pillow to be installed.
        """
        self.to_pillow().show()
