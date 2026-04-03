"""
pictex: A Python library for creating complex visual compositions and beautifully styled images.
"""

from . import __skia_init
__skia_init.prime_skia_icu_engine()

from .builders import Canvas, Text, Row, Column, Image, Element, Span
from .models.public import *
from .bitmap_image import BitmapImage
from .vector_image import VectorImage

__version__ = "2.3.0"

__all__ = [
    "Canvas", "Text", "Row", "Column", "Image", "Element", "Span",
    
    "Shadow", "OutlineStroke", "StrokeMode",
    "Style",
    "FontStyle", "FontWeight", "FontSmoothing", "TextAlign", "TextWrap",
    "TextDirection",
    "PaintSource",
    "SolidColor", "NamedColor",
    "LinearGradient",
    "RadialGradient",
    "SweepGradient",
    "TwoPointConicalGradient",
    "TextDecoration",
    "CropMode",
    "Box",
    "Position", "PositionType", "Inset",
    "Transform",
    "SizeValue", "SizeValueMode",
    "Margin", "Padding", "JustifyContent", "AlignItems", "AlignSelf", "FlexWrap",
    "BackgroundImage", "BackgroundImageSizeMode",
    "Border", "BorderStyle", "BorderRadiusValue", "BorderRadius",
    "RenderNode",
    "NodeType",
    "LineHeight", "LineHeightMode",
    "Overflow",

    "BitmapImage",
    "VectorImage",
]