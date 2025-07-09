from dataclasses import dataclass, field
from .color import SolidColor
from .paint_source import PaintSource

@dataclass
class Background:
    """Represents a background shape behind the text."""
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0, 0))
    corner_radius: float = 0.0
