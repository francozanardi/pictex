import logging

logger = logging.getLogger("pictex")
logger.addHandler(logging.NullHandler())

from .canvas import Canvas
from .models.style import Style
from .models.color import Color
from .models.effects import Shadow
from .models.typography import Font, Alignment, FontStyle, FontWeight
from .models.linear_gradient import LinearGradient

__version__ = "0.1.0"

__all__ = [
    "Canvas",
    "Style",
    "Color",
    "LinearGradient",
    "Shadow",
    "Font",
    "Alignment",
    "FontStyle",
    "FontWeight",
]
