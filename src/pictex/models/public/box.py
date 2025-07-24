from dataclasses import dataclass

@dataclass(frozen=True)
class Box:
    """Represents a rectangular area with position and size."""
    x: int
    y: int
    width: int
    height: int
