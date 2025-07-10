from __future__ import annotations
from typing import Optional, overload, Union

from .models import *
from .image import Image
from .renderer import SkiaRenderer

class Canvas:
    """
    The main user-facing class for creating stylized text images.

    This class implements a fluent builder pattern to define a style template,
    which can then be used to render multiple texts.
    """
    def __init__(self, style: Optional[Style] = None):
        """Initializes a new Canvas with an optional base style."""
        self._style = style if style is not None else Style()

    def font_family(self, family: str) -> Canvas:
        """Sets the font family or a path to a font file. Returns self for chaining."""
        self._style.font.family = family
        return self
    
    def font_fallbacks(self, *fonts: str) -> Canvas:
        """
        Specifies a list of fallback fonts to use for characters not supported
        by the primary font. Can be font names or paths to font files.
        """
        self._style.font_fallbacks = list(fonts)
        return self
    
    def font_size(self, size: float) -> Canvas:
        """Sets the font size in points. Returns self for chaining."""
        self._style.font.size = size
        return self
    
    def font_weight(self, weight: FontWeight | int) -> Canvas:
        """Sets the font weight (e.g., FontWeight.BOLD or 700). Returns self for chaining."""
        self._style.font.weight = weight if isinstance(weight, FontWeight) else FontWeight(weight)
        return self
    
    def font_style(self, style: FontStyle | str) -> Canvas:
        """Sets the font style (e.g., FontStyle.ITALIC). Returns self for chaining."""
        self._style.font.style = style if isinstance(style, FontStyle) else FontStyle(style)
        return self

    def color(self, color: str | PaintSource) -> Canvas:
        """Sets the primary text color or gradient. Returns self for chaining."""
        self._style.color = self.__build_color(color)
        return self

    def add_shadow(self, offset: tuple[float, float], blur_radius: float = 0, color: str | SolidColor = 'black') -> Canvas:
        """Adds a text shadow effect. Can be called multiple times. Returns self for chaining."""
        shadow_color = self.__build_color(color)
        self._style.shadows.append(Shadow(offset, blur_radius, shadow_color))
        return self
    
    def add_box_shadow(self, offset: tuple[float, float], blur_radius: float = 0, color: str | SolidColor = 'black') -> Canvas:
        """Adds a background box shadow. Can be called multiple times. Returns self for chaining."""
        shadow_color = self.__build_color(color)
        self._style.box_shadows.append(Shadow(offset, blur_radius, shadow_color))
        return self
    
    def outline_stroke(self, width: float, color: str | PaintSource) -> Canvas:
        """Adds an outline stroke to the text. Returns self for chaining."""
        self._style.outline_stroke = OutlineStroke(width=width, color=self.__build_color(color))
        return self
    
    def underline(self, thickness: float = 2.0, color: Optional[str | PaintSource] = None) -> Canvas:
        """Adds an underline text decoration. Returns self for chaining."""
        color = self.__build_color(color) if color else None
        self._style.decorations.append(
            TextDecoration(line=DecorationLine.UNDERLINE, color=color, thickness=thickness)
        )
        return self
    
    def strikethrough(self, thickness: float = 2.0, color: Optional[str | PaintSource] = None) -> Canvas:
        """Adds a strikethrough text decoration. Returns self for chaining."""
        color = self.__build_color(color) if color else None
        self._style.decorations.append(
            TextDecoration(line=DecorationLine.STRIKETHROUGH, color=color, thickness=thickness)
        )
        return self

    @overload
    def padding(self, all: float) -> Canvas: ...
    @overload
    def padding(self, vertical: float, horizontal: float) -> Canvas: ...
    @overload
    def padding(self, top: float, right: float, bottom: float, left: float) -> Canvas: ...
    def padding(self, *args: Union[float, int]) -> Canvas:
        """
        Sets padding around the text. Supports 1, 2, or 4 values like CSS.

        - 1 value: all sides
        - 2 values: vertical, horizontal
        - 4 values: top, right, bottom, left

        Returns:
            The Canvas instance for chaining.
        """
        if len(args) == 1:
            value = float(args[0])
            self._style.padding = (value, value, value, value)
        elif len(args) == 2:
            vertical = float(args[0])
            horizontal = float(args[1])
            self._style.padding = (vertical, horizontal, vertical, horizontal)
        elif len(args) == 4:
            top, right, bottom, left = map(float, args)
            self._style.padding = (top, right, bottom, left)
        else:
            raise TypeError(f"padding() takes 1, 2 or 4 arguments but got {len(args)}")
        
        return self

    def background_color(self, color: str | PaintSource) -> Canvas:
        """Sets the background color or gradient. Returns self for chaining."""
        self._style.background.color = self.__build_color(color)
        return self

    def background_radius(self, radius: float) -> Canvas:
        """Sets the corner radius for the background. Returns self for chaining."""
        self._style.background.corner_radius = radius
        return self
    
    def line_height(self, multiplier: float) -> Canvas:
        """
        Sets the line height as a multiplier of the font size. Returns self for chaining.
        (e.g., 1.5 means 150% line spacing).
        """
        self._style.font.line_height = multiplier
        return self
    
    def alignment(self, alignment: Alignment | str) -> Canvas:
        """Sets the text alignment for multi-line text. Returns self for chaining."""
        self._style.alignment = alignment if isinstance(alignment, Alignment) else Alignment(alignment)
        return self
    
    def font_smoothing(self, mode: FontSmoothing | str) -> Canvas:
        """
        Sets the font anti-aliasing strategy.
        
        Args:
            mode: Accepts either `FontSmoothing.SUBPIXEL` or `FontSmoothing.STANDARD`, 
              or their string equivalents ("subpixel" or "standard").
 
        Returns:
            The Canvas instance for chaining.
        """
        self._style.font.smoothing = mode if isinstance(mode, FontSmoothing) else FontSmoothing(mode)
        return self
    
    def render(self, text: str, crop_mode: CropMode = CropMode.NONE) -> Image:
        """
        Renders an image from the given text using the configured style.
        
        Args:
            text: The text string to render. Can contain newlines (`\\n`).
            crop_mode: The cropping strategy for the final canvas.
                  - SMART: Tightly crops to only visible pixels.
                  - CONTENT_BOX: Crops to the text + padding area.
                  - NONE: No cropping, includes all effect boundaries (default).
        
        Returns:
            An `Image` object containing the rendered result.
        """
        renderer = SkiaRenderer(self._style)
        skia_image, content_box = renderer.render(text, crop_mode)
        return Image(skia_image, content_box)

    def __build_color(self, color: str | PaintSource) -> PaintSource:
        """Internal helper to create a SolidColor from a string or return it as is."""
        return SolidColor.from_str(color) if isinstance(color, str) else color
