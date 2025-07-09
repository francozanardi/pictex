import logging

logger = logging.getLogger("pictex")
logger.addHandler(logging.NullHandler())

from .canvas import Canvas
from .models import *
from .image import Image

__version__ = "0.1.0"

__all__ = [
    "Canvas",
    "Style",
    "Color",
    "LinearGradient",
    "Background",
    "Shadow",
    "OutlineStroke",
    "Font",
    "Alignment",
    "FontStyle",
    "FontWeight",
    "DecorationLine",
    "TextDecoration",
    "Image",
    "CropMode",
    "Box",
]
