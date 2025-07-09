from dataclasses import dataclass
from enum import Enum
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

@dataclass
class Font:
    """Represents font properties."""
    family: str = "Arial"
    """
    The font family. Can be a system font name (e.g., "Arial", "Times New Roman")
    or a path to a font file (e.g., "path/to/my_font.ttf").
    """
    size: float = 50.0
    line_height: float = 1.0  # Multiplier for the font size, like in CSS

    weight: FontWeight = FontWeight.NORMAL
    slant: FontStyle = FontStyle.NORMAL
