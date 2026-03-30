from dataclasses import dataclass
from enum import Enum


class TextBoxEdgeValue(str, Enum):
    """Determines how a single edge of a text node's box is calculated.

    - ``FONT``: Uses the font's ascent/descent metrics. The box size is fixed
      and determined solely by the font, making layouts stable and predictable
      regardless of the text content.
    - ``GLYPHS``: Uses the actual ink bounds of the rendered glyphs. The box
      tightly wraps the visible characters, but the box size becomes
      content-dependent - different strings will produce different sizes.
    """
    FONT = "font"
    GLYPHS = "glyphs"


@dataclass
class TextBoxEdge:
    """Defines how the top and bottom edges of a text node's box are calculated."""
    top: TextBoxEdgeValue = TextBoxEdgeValue.FONT
    bottom: TextBoxEdgeValue = TextBoxEdgeValue.FONT

@dataclass
class Margin:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

@dataclass
class Padding:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

class JustifyContent(str, Enum):
    """Main-axis distribution for flex containers (CSS justify-content)."""
    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"

class AlignItems(str, Enum):
    """Cross-axis alignment for flex containers (CSS align-items)."""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"

class AlignSelf(str, Enum):
    """Self-alignment override for flex items (CSS align-self)."""
    AUTO = "auto"
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"

class FlexWrap(str, Enum):
    """Flex wrapping behavior (CSS flex-wrap)."""
    NOWRAP = "nowrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap-reverse"
