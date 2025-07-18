from dataclasses import dataclass
from typing import Sequence, Optional
import skia

from .paint_source import PaintSource
from .color import SolidColor

@dataclass
class LinearGradient(PaintSource):
    """
    Represents a linear gradient fill, smoothly transitioning between colors
    along a straight line.

    The gradient's direction and color distribution are controlled by its
    parameters. This class allows for creating rich, colorful fills for
    text and backgrounds.

    Attributes:
        colors (Sequence[Color]): A sequence of two or more Color objects
            that define the key colors of the gradient.
        stops (Optional[Sequence[float]]): A sequence of numbers between 0.0
            and 1.0 that specify the position of each color in the `colors`
            sequence. The length of `stops` must match the length of `colors`.
            If `None`, the colors are distributed evenly along the gradient line.
            For example, for `colors` with 3 colors, `stops=[0.0, 0.5, 1.0]`
            would place the second color exactly in the middle of the gradient.
        start_point (tuple[float, float]): A tuple `(x, y)` representing the
            starting point of the gradient line. Coordinates are relative to the
            object's bounding box, where (0.0, 0.0) is the top-left corner and
            (1.0, 1.0) is the bottom-right corner.
        end_point (tuple[float, float]): A tuple `(x, y)` representing the
            ending point of the gradient line. The gradient is drawn along the
            line connecting `start_point` to `end_point`.

    Example:
        # A simple horizontal gradient from red to blue
        ```python
        horizontal_gradient = LinearGradient(
            colors=['#FF0000', 'blue']
        )
        ```

        # A vertical gradient from top (yellow) to bottom (orange)
        ```python
        vertical_gradient = LinearGradient(
            colors=['yellow', 'orange'],
            start_point=(0.5, 0.0),
            end_point=(0.5, 1.0)
        )
        ```

        # A diagonal gradient with a custom color stop
        ```python
        diagonal_gradient = LinearGradient(
            colors=[
                'magenta',
                'cyan',
                'yellow'
            ],
            stops=[0.0, 0.2, 1.0] # 'cyan' is positioned 20% along the gradient
        )
        ```
    """
    colors: Sequence[SolidColor]
    stops: Optional[Sequence[float]] = None
    start_point: tuple[float, float] = (0.0, 0.5)
    end_point: tuple[float, float] = (1.0, 0.5)

    def __post_init__(self):
        self.colors = [
            SolidColor.from_str(c) if isinstance(c, str) else c
            for c in self.colors
        ]
        if not all(isinstance(c, SolidColor) for c in self.colors):
             raise TypeError("All items in 'colors' must be Color objects or valid color strings.")

    def apply_to_paint(self, paint: skia.Paint, bounds: skia.Rect) -> None:
        """Creates a linear gradient shader and applies it to the paint."""
        if not self.colors:
            return

        skia_colors = [skia.Color(c.r, c.g, c.b, c.a) for c in self.colors]
        
        # Convert relative points to absolute coordinates based on the bounds
        p1 = (
            bounds.left() + self.start_point[0] * bounds.width(),
            bounds.top() + self.start_point[1] * bounds.height()
        )
        p2 = (
            bounds.left() + self.end_point[0] * bounds.width(),
            bounds.top() + self.end_point[1] * bounds.height()
        )

        shader = skia.GradientShader.MakeLinear(
            points=[p1, p2],
            colors=skia_colors,
            positions=self.stops
        )
        paint.setShader(shader)
