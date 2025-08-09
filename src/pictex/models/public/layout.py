from dataclasses import dataclass
from enum import Enum

@dataclass
class Margin:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

@dataclass
class Padding:
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0

class HorizontalDistribution(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"

class VerticalAlignment(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    STRETCH = "stretch"

class VerticalDistribution(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"

class HorizontalAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    STRETCH = "stretch"

