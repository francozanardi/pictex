from dataclasses import dataclass, field
from .color import SolidColor
from .paint_source import PaintSource

@dataclass
class Shadow:
    """Represents a drop shadow effect."""
    offset: tuple[float, float] = (2, 2)
    blur_radius: float = 4.0
    color: SolidColor = field(default_factory=lambda: SolidColor(0, 0, 0, a=128))

@dataclass
class OutlineStroke:
    """Represents an outline text stroke."""
    width: float = 2.0
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0))
