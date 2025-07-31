from dataclasses import dataclass, field
from .color import SolidColor
from .paint_source import PaintSource

@dataclass
class Shadow:
    """Represents a drop shadow effect for an element.

    Attributes:
        offset (tuple[float, float]): A tuple `(dx, dy)` specifying the
            horizontal and vertical offset of the shadow from the element.
            Positive `dx` values shift the shadow to the right, and positive
            `dy` values shift it downward. Defaults to `(2, 2)`.
        blur_radius (float): The radius of the Gaussian blur applied to the
            shadow's shape. Larger values create a softer, more diffused
            shadow, while a value of 0 results in a sharp, un-blurred shadow.
            Defaults to `2.0`.
        color (SolidColor|str): The color of the shadow, specified as a
            string or a `SolidColor` object. Defaults to a semi-transparent black,
            equivalent to `rgba(0, 0, 0, 0.5)`.

    Example:
        ```python
        from pictex import Text, Shadow

        # A soft, standard drop shadow for a box
        soft_shadow = Shadow(
            offset=(3, 3),
            blur_radius=5,
            color="black"
        )

        # Applying a single shadow to a box
        element_with_shadow = Row().box_shadows(soft_shadow)

        # Applying multiple shadows to text for a neon glow effect
        neon_text = Text("Glow").text_shadows(
            Shadow(blur_radius=4, color="cyan"),
            Shadow(blur_radius=8, color="magenta"),
            Shadow(blur_radius=12, color="blue")
        )
        ```
    """
    offset: tuple[float, float] = (2, 2)
    blur_radius: float = 2.0
    color: SolidColor = field(default_factory=lambda: SolidColor(0, 0, 0, a=128))

    def __post_init__(self):
        self.color = SolidColor.from_str(self.color) if isinstance(self.color, str) else self.color
        if not isinstance(self.color, SolidColor):
             raise TypeError("Argument 'color' must be a SolidColor object or a valid color string.")

@dataclass
class OutlineStroke:
    """Represents an outline text stroke."""
    width: float = 2.0
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0))
