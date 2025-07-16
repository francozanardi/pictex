from dataclasses import dataclass, field
from typing import Optional

from .color import SolidColor
from .effects import Shadow, OutlineStroke
from .typography import Font, Alignment
from .background import Background
from .paint_source import PaintSource
from .decoration import TextDecoration

@dataclass
class Style:
    """
    A comprehensive container for all text styling properties.
    This is the core data model for the library.
    """
    font: Font = field(default_factory=Font)
    font_fallbacks: list[str] = field(default_factory=list)
    alignment: Alignment = Alignment.LEFT
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0))
    shadows: list[Shadow] = field(default_factory=list)
    box_shadows: list[Shadow] = field(default_factory=list)
    outline_stroke: Optional[OutlineStroke] = None
    padding: tuple[float, float, float, float] = (10, 10, 10, 10) # Top, Right, Bottom, Left
    background: Background = field(default_factory=Background)
    decorations: list[TextDecoration] = field(default_factory=list)
