from abc import ABC, abstractmethod
import skia

class PaintSource(ABC):
    """
    Abstract base class for anything that can be used as a source for a skia.Paint.
    This includes solid colors, gradients, patterns, etc.
    """
    
    @abstractmethod
    def apply_to_paint(self, paint: skia.Paint, bounds: skia.Rect) -> None:
        """
        Configures the given skia.Paint object to use this source.

        Args:
            paint: The skia.Paint object to modify.
            bounds: The bounding box of the shape being painted. This is crucial
                    for calculating relative coordinates for gradients.
        """
        pass
