from enum import Enum
import skia

class TextAlign(str, Enum):
    """Text alignment options. Useful in multi-line text blocks."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class FontStyle(str, Enum):
    """Represents the builders of a font. Useful for variable fonts. """
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
    """Defines the antialiasing strategy for text rendering."""
    SUBPIXEL = "subpixel"
    STANDARD = "standard"
