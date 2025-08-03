from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .color import SolidColor

@dataclass
class TextDecoration:
    """Represents a line drawn over, under, or through the text."""
    color: Optional[SolidColor] = None  # If None, use the text's color.
    thickness: float = 4.0
