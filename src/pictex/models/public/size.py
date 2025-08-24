from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

class SizeValueMode(str, Enum):
    AUTO = 'auto'
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
    FIT_CONTENT = 'fit-content'
    FILL_AVAILABLE = 'fill-available'
    FIT_BACKGROUND_IMAGE = 'fit-background-image'

class SizeValue(NamedTuple):
    mode: SizeValueMode
    value: float = 0
