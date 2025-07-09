from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .color import Color

class DecorationLine(Enum):
    """The type of line to draw for the decoration."""
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"

@dataclass
class TextDecoration:
    """Represents a line drawn over, under, or through the text."""
    line: DecorationLine
    color: Optional[Color] = None  # If None, use the text's color.
    thickness: float = 4.0
