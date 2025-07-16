"""
pictex: A Python library for creating beautifully styled text images.

This package provides a simple, fluent API to generate images from text,
with powerful styling options like gradients, shadows, and custom fonts.
"""

from .canvas import Canvas
from .models import *
from .image import Image
from .vector_image import VectorImage

__version__ = "0.3.0"

__all__ = [
    "Canvas",
    "Style",
    "SolidColor",
    "LinearGradient",
    "Background",
    "Shadow",
    "OutlineStroke",
    "Font",
    "FontSmoothing",
    "Alignment",
    "FontStyle",
    "FontWeight",
    "DecorationLine",
    "TextDecoration",
    "Image",
    "VectorImage",
    "CropMode",
    "Box",
]
