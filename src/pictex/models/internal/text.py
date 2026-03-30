from dataclasses import dataclass, field
from typing import Optional
import skia
from ...models import TextDirection, Style


@dataclass
class ShapedGlyph:
    """A single shaped glyph with positioning information in points."""
    glyph_id: int
    cluster: int
    x_advance: float
    y_advance: float
    x_offset: float
    y_offset: float

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
    strikethrough_position: float

@dataclass(frozen=True)
class LineMetrics:
    height: float
    baseline: float # distance from top of line to baseline
    underline: float # distance from top of line to underline position
    strikethrough: float # distance from top of line to strikethrough position

@dataclass
class SpanInfo:
    """Carries the style shared by all TextRuns originating from the same span.

    Multiple runs can point to the same SpanInfo instance when they come from
    the same span but were split by font-fallback or BiDi boundaries. Object
    identity (``is`` / ``id()``) is used to group co-span runs so that gradient
    bounds can be computed over the full span extent rather than per-run.
    """
    computed_style: Style  # The fully evaluated style, completely filled in with inherited properties.
    explicit_style: Optional[Style] = None  # The style containing only properties explicitly set on the span itself.


@dataclass
class TextRun:
    """Represents a segment of text that can be rendered with a single font."""
    text: str
    font: skia.Font
    bidi_fragment: BiDiFragment
    span: SpanInfo
    fragment_offset: int = 0  # char offset within bidi_fragment.text where this run starts
    shaped_glyphs: list[ShapedGlyph] = field(default_factory=list)
    blob: Optional[skia.TextBlob] = None
    width: float = 0.0

    @property
    def style(self) -> Style:
        return self.span.computed_style

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
    metrics: LineMetrics
