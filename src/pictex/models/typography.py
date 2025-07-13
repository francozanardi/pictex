from dataclasses import dataclass
from enum import Enum
from typing import Optional
import skia

class Alignment(str, Enum):
    """Text alignment options. Useful in multi-line text blocks."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class FontStyle(str, Enum):
    """Represents the style of a font. Useful for variable fonts. """
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"

    def to_skia_slant(self):
        SLANT_MAP = {
            FontStyle.NORMAL: skia.FontStyle.kUpright_Slant,
            FontStyle.ITALIC: skia.FontStyle.kItalic_Slant,
            FontStyle.OBLIQUE: skia.FontStyle.kOblique_Slant,
        }
        return SLANT_MAP[self.value]

class FontWeight(int, Enum):
    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    BLACK = 900

class FontSmoothing(str, Enum):
    """Defines the anti-aliasing strategy for text rendering."""
    SUBPIXEL = "subpixel"
    STANDARD = "standard"

@dataclass
class Font:
    """Represents font properties."""
    family: Optional[str] = None
    """
    The font family. Can be a system font name (e.g., "Arial"), a path
    to a font file, or None to use the system's default font.
    """
    size: float = 50.0
    line_height: float = 1.0  # Multiplier for the font size, like in CSS

    weight: FontWeight = FontWeight.NORMAL
    style: FontStyle = FontStyle.NORMAL

    smoothing: FontSmoothing = FontSmoothing.SUBPIXEL
