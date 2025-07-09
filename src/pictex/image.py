from __future__ import annotations
import skia
import numpy as np

class Image:
    """
    A wrapper around a rendered Skia image.

    This class provides convenient methods to access image data, save to a file,
    or convert to other popular formats like NumPy arrays or Pillow images.
    """
    def __init__(self, skia_image: skia.Image):
        self._skia_image = skia_image

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

    def save(self, output_path: str) -> None:
        """
        Saves the image to a file. The format is inferred from the extension.
        
        Args:
            output_path: The path to save the output image (e.g., 'image.png').
        """
        self._skia_image.save(output_path)
        
    def show(self) -> None:
        """
        Displays the image using Pillow. Useful for debugging in scripts.
        Requires Pillow to be installed.
        """
        self.to_pillow().show()
