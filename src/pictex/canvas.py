# src/glyphcraft/crafter.py
from __future__ import annotations
from typing import Optional

from .models import Style, Color, Shadow, Alignment, FontWeight, FontStyle, TextDecoration, DecorationLine, PaintSource, OutlineStroke
from .renderer import SkiaRenderer

class Canvas:
    """
    The main user-facing class for creating stylized text images.
    Implements a fluent builder pattern.
    """
    def __init__(
        self,
        style: Optional[Style] = None,
    ):
        self.style = style if style is not None else Style()
        self._renderer = SkiaRenderer()

    def font_family(self, family: str) -> Canvas:
        self.style.font.family = family
        return self
    
    def font_size(self, size: float) -> Canvas:
        self.style.font.size = size
        return self
    
    def font_weight(self, weight: FontWeight | int) -> Canvas:
        self.style.font.weight = weight if isinstance(weight, FontWeight) else FontWeight(weight)
        return self
    
    def font_style(self, style: FontStyle | str) -> Canvas:
        self.style.font.slant = style if isinstance(style, FontStyle) else FontStyle(style)
        return self

    def color(self, color: str | PaintSource) -> Canvas:
        self.style.color = self.__build_color(color)
        return self

    def shadow(self, offset: tuple[float, float], blur_radius: float, color: str | Color) -> Canvas:
        shadow_color = self.__build_color(color)
        self.style.shadow = Shadow(offset, blur_radius, shadow_color)
        return self
    
    def outline_stroke(self, width: float, color: str | PaintSource) -> Canvas:
        """Adds an outline stroke to the text."""
        self.style.outline_stroke = OutlineStroke(width=width, color=self.__build_color(color))
        return self
    
    def underline(self, thickness: float = 2.0, color: Optional[str | PaintSource] = None) -> Canvas:
        color = self.__build_color(color) if color else None
        self.style.decorations.append(
            TextDecoration(line=DecorationLine.UNDERLINE, color=color, thickness=thickness)
        )
        return self
    
    def strikethrough(self, thickness: float = 2.0, color: Optional[str | PaintSource] = None) -> Canvas:
        color = self.__build_color(color) if color else None
        self.style.decorations.append(
            TextDecoration(line=DecorationLine.STRIKETHROUGH, color=color, thickness=thickness)
        )
        return self

    def padding(self, left: float, top: float, right: float, bottom: float) -> Canvas:
        self.style.padding = (left, top, right, bottom)
        return self

    def background_color(self, color: str | PaintSource) -> Canvas:
        self.style.background.color = self.__build_color(color)
        return self

    def background_radius(self, radius: float) -> Canvas:
        self.style.background.corner_radius = radius
        return self
    
    def line_height(self, multiplier: float) -> Canvas:
        """
        Sets the line height as a multiplier of the font size.
        E.g., 1.5 means 150% line spacing.
        """
        self.style.font.line_height = multiplier
        return self
    
    def alignment(self, alignment: Alignment | str) -> Canvas:
        self.style.alignment = alignment if isinstance(alignment, Alignment) else Alignment(alignment)
        return self
    
    def render(self, text: str):
        """Renders the image and returns a Skia Image object."""
        return self._renderer.render(text, self.style)

    def __build_color(self, color: str | PaintSource) -> PaintSource:
        return Color.from_str(color) if isinstance(color, str) else color
