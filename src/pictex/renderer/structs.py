from dataclasses import dataclass
import skia
from enum import Enum
from typing import Optional

@dataclass
class TextRun:
    """Represents a segment of text that can be rendered with a single font."""
    text: str
    font: skia.Font
    width: float = 0.0

@dataclass
class Line:
    """Represents a full line composed of multiple TextRuns."""
    runs: list[TextRun]
    width: float
    bounds: skia.Rect

@dataclass
class RenderMetrics:
    """A helper class to store all calculated dimensions for rendering."""
    bounds: skia.Rect
    background_rect: skia.Rect
    text_rect: skia.Rect
    draw_origin: tuple[float, float]

class TypefaceSource(str, Enum):
    SYSTEM = "system"
    FILE = "file"

@dataclass
class TypefaceLoadingInfo:
    typeface: skia.Typeface
    source: TypefaceSource
    filepath: Optional[str] # only valid on 'file' fonts
