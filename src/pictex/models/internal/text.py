from dataclasses import dataclass
from typing import Optional
import skia
from ..public.text_direction import TextDirection

@dataclass
class BiDiFragment:
    """
    A chunk of text sharing a uniform text direction.
    It represents a logical piece of the original text, sequenced
    in its final visual left-to-right drawing order.
    """
    text: str
    direction: TextDirection
    start_index: int

@dataclass(frozen=True)
class FontMetrics:
    ascent: float
    descent: float
    leading: float
    underline_position: float
    strikeout_position: float

@dataclass
class TextRun:
    """Represents a segment of text that can be rendered with a single font."""
    text: str
    font: skia.Font
    metrics: FontMetrics
    bidi_fragment: BiDiFragment
    fragment_offset: int = 0  # char offset within bidi_fragment.text where this run starts
    blob: Optional[skia.TextBlob] = None
    width: float = 0.0

    @property
    def direction(self) -> TextDirection:
        return self.bidi_fragment.direction

@dataclass
class Line:
    """Represents a full line composed of multiple TextRuns."""
    runs: list[TextRun]
    width: float
    height: float
    bounds: skia.Rect
    metrics: FontMetrics
