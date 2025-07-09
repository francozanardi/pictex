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
class Color(PaintSource):
    """Represents a solid RGBA color."""
    r: int
    g: int
    b: int
    a: int = 255

    @classmethod
    def from_hex(cls, hex_str: str) -> Color:
        """Creates a Color object from a hex string (e.g., '#RRGGBB' or '#RGB')."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)
        if len(hex_str) != 6:
            raise ValueError("Invalid hex color format.")
        
        r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return cls(r, g, b)

    @classmethod
    def from_str(cls, value: str) -> Color:
        """
        Creates a Color object from a string.
        Supports hex codes (e.g., '#ff0000') and named colors (e.g., 'red').
        """
        hex_code = value.strip().lower() if value.startswith('#') else NAMED_COLORS.get(value, None)
        if hex_code:
            return cls.from_hex(hex_code)
        
        raise ValueError(f"Unknown color name or format: '{value}'")

    def apply_to_paint(self, paint: skia.Paint, bounds: skia.Rect) -> None:
        """Applies this solid color to the paint object."""
        paint.setColor(skia.Color(self.r, self.g, self.b, self.a))
