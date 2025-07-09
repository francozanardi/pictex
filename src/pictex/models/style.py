from dataclasses import dataclass, field
from typing import Optional

from .color import Color
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
    alignment: Alignment = Alignment.LEFT
    color: PaintSource = field(default_factory=lambda: Color(0, 0, 0))
    shadow: Optional[Shadow] = None
    outline_stroke: Optional[OutlineStroke] = None
    padding: tuple[float, float, float, float] = (5, 5, 5, 5) # Top, Right, Bottom, Left
    background: Background = field(default_factory=Background)
    decorations: list[TextDecoration] = field(default_factory=list)
