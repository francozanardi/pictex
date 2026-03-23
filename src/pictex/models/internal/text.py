from dataclasses import dataclass
from typing import Optional
import skia

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
    blob: Optional[skia.TextBlob] = None
    width: float = 0.0

@dataclass
class Line:
    """Represents a full line composed of multiple TextRuns."""
    runs: list[TextRun]
    width: float
    height: float
    bounds: skia.Rect
    metrics: FontMetrics
