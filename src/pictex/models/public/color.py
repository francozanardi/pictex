from __future__ import annotations
from dataclasses import dataclass
import skia

from .paint_source import PaintSource

NAMED_COLORS = {
    'black': '#000000',
    'white': '#ffffff',
    'red': '#ff0000',
    'green': '#008000',
    'blue': '#0000ff',
    'yellow': '#ffff00',
    'cyan': '#00ffff',
    'magenta': '#ff00ff',
    'silver': '#c0c0c0',
    'gray': '#808080',
    'maroon': '#800000',
    'olive': '#808000',
    'purple': '#800080',
    'teal': '#008080',
    'navy': '#000080',
    'orange': '#ffa500',
    'gold': '#ffd700',
    'pink': '#ffc0cb',
}


@dataclass(frozen=True)
class SolidColor(PaintSource):
    """Represents a solid color with RGBA components.

    This class provides a structured way to handle solid colors, with methods
    for creating instances from various string formats like hex codes or
    standard color names.

    Attributes:
        r (int): The red component of the color (0-255).
        g (int): The green component of the color (0-255).
        b (int): The blue component of the color (0-255).
        a (int): The alpha (opacity) component of the color (0-255), where
            255 is fully opaque. Defaults to 255.
    """
    r: int
    g: int
    b: int
    a: int = 255

    @classmethod
    def _from_hex(cls, hex_str: str) -> SolidColor:
        """Creates a SolidColor object from a hexadecimal string.

        Supports various hex formats: '#RGB', '#RRGGBB', and '#RRGGBBAA'.

        Args:
            hex_str: The hexadecimal color string.

        Returns:
            A new `SolidColor` instance.

        Raises:
            ValueError: If the hex string format is invalid.
        """
        hex_str = hex_str.lstrip('#')

        if len(hex_str) == 3:  # Expand short form like #F0C to #FF00CC
            hex_str = "".join(c * 2 for c in hex_str)

        if len(hex_str) == 8:  # RRGGBBAA
            r, g, b, a = (int(hex_str[i:i + 2], 16) for i in (0, 2, 4, 6))
            return cls(r, g, b, a)
        elif len(hex_str) == 6:  # RRGGBB
            r, g, b = (int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
            return cls(r, g, b)
        else:
            raise ValueError(f"Invalid hex color format: '{hex_str}'")

    @classmethod
    def from_str(cls, value: str) -> SolidColor:
        """Creates a SolidColor object from a general color string.

        This method acts as a factory, supporting standard color names
        (e.g., 'red', 'blue') and hexadecimal codes.

        Args:
            value: The color string to parse.

        Returns:
            A new `SolidColor` instance.

        Raises:
            ValueError: If the color name is unknown or the format is invalid.
        """
        clean_value = value.strip().lower()
        if clean_value.startswith('#'):
            return cls._from_hex(clean_value)

        hex_code = NAMED_COLORS.get(clean_value)
        if hex_code:
            return cls._from_hex(hex_code)

        raise ValueError(f"Unknown color name or format: '{value}'")

    def apply_to_paint(self, paint: skia.Paint, bounds: skia.Rect) -> None:
        """Applies this solid color to a Skia Paint object.

        This method is part of the `PaintSource` interface and is used by the
        rendering engine.

        Args:
            paint: The `skia.Paint` object to modify.
            bounds: The bounding box of the area to be painted. This is not
                used for solid colors but is part of the interface for
                compatibility with gradients.
        """
        paint.setColor(skia.Color(self.r, self.g, self.b, self.a))