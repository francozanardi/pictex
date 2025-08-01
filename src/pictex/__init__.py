"""
pictex: A Python library for creating beautifully styled text images.

This package provides a simple, fluent API to generate images from text,
with powerful styling options like gradients, shadows, and custom fonts.
"""

from .builders import Canvas, Text, Row, Column, Image
from .models.public import *
from .bitmap_image import BitmapImage
from .vector_image import VectorImage

__version__ = "0.3.0"

__all__ = [
    "Canvas",
    "Text",
    "Row",
    "Column",
    "Image",
    "Style",
    "SolidColor",
    "LinearGradient",
    "Shadow",
    "OutlineStroke",
    "FontSmoothing",
    "TextAlign",
    "FontStyle",
    "FontWeight",
    "TextDecoration",
    "BitmapImage",
    "VectorImage",
    "CropMode",
    "Box",
    "Padding",
    "Margin",
    "Border",
    "BorderRadius",
    "BorderRadiusValue",
    "BackgroundImage",
    "BackgroundImageSizeMode",
    "Size",
    "SizeValue",
    "SizeValueMode",
    "Position",
    "PositionMode",
    "HorizontalDistribution",
    "HorizontalAlignment",
    "VerticalDistribution",
    "VerticalAlignment",
]
