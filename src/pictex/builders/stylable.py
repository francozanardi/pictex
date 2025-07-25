from __future__ import annotations
from typing import Optional, Union, overload, Self
from pathlib import Path
from ..models import *

class Stylable:

    def __init__(self):
        self._style = Style()

    def font_family(self, family: Union[str, Path]) -> Self:
        """Sets the font family or a path to a font file.

        Args:
            family: The name of the font family or a `Path` object to a font file.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_family.set(str(family))
        return self

    def font_fallbacks(self, *fonts: Union[str, Path]) -> Self:
        """Specifies a list of fallback fonts.

        These fonts are used for characters not supported by the primary font.

        Args:
            *fonts: A sequence of font names or `Path` objects to font files.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_fallbacks.set([str(font) for font in fonts])
        return self

    def font_size(self, size: float) -> Self:
        """Sets the font size in points.

        Args:
            size: The new font size.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_size.set(size)
        return self

    def font_weight(self, weight: Union[FontWeight, int]) -> Self:
        """Sets the font weight.

        Args:
            weight: The font weight, e.g., `FontWeight.BOLD` or `700`.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_weight.set(weight if isinstance(weight, FontWeight) else FontWeight(weight))
        return self

    def font_style(self, style: Union[FontStyle, str]) -> Self:
        """Sets the font builders.

        Args:
            style: The font builders, e.g., `FontStyle.ITALIC`.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_style.set(style if isinstance(style, FontStyle) else FontStyle(style))
        return self

    def line_height(self, multiplier: float) -> Self:
        """Sets the line height as a multiplier of the font size.

        For example, a value of 1.5 corresponds to 150% line spacing.

        Args:
            multiplier: The line height multiplier.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.line_height.set(multiplier)
        return self

    # TODO: rename to text_color?
    def color(self, color: Union[str, PaintSource]) -> Self:
        """Sets the text color or gradient.

        Args:
            color: A color string (e.g., "red", "#FF0000") or a `PaintSource` object.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.color.set(self._build_color(color))
        return self

    # TODO: rename to text_shadow() and support multiple Shadow objects.
    def add_shadow(
        self,
        offset: tuple[float, float],
        blur_radius: float = 0,
        color: Union[str, SolidColor] = 'black'
    ) -> Self:
        """Adds a text shadow effect.

        This method can be called multiple times to add multiple shadows.

        Args:
            offset: A tuple `(dx, dy)` for the shadow's offset.
            blur_radius: The blur radius of the shadow.
            color: The color of the shadow.

        Returns:
            The `Self` instance for chaining.
        """
        shadow_color = self._build_color(color)
        self._style.text_shadows.set([Shadow(offset, blur_radius, shadow_color)])
        return self

    # TODO: rename to box_shadow() and support multiple Shadow objects.
    def add_box_shadow(
        self,
        offset: tuple[float, float],
        blur_radius: float = 0,
        color: Union[str, SolidColor] = 'black'
    ) -> Self:
        """Adds a background box shadow.

        This method can be called multiple times to add multiple shadows.

        Args:
            offset: A tuple `(dx, dy)` for the shadow's offset.
            blur_radius: The blur radius of the shadow.
            color: The color of the shadow.

        Returns:
            The `Self` instance for chaining.
        """
        shadow_color = self._build_color(color)
        self._style.box_shadows.set([Shadow(offset, blur_radius, shadow_color)])
        return self

    def outline_stroke(self, width: float, color: Union[str, PaintSource]) -> Self:
        """Adds an outline stroke to the text.

        Args:
            width: The width of the outline stroke.
            color: The color of the outline.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.outline_stroke.set(OutlineStroke(width=width, color=self._build_color(color)))
        return self

    def underline(
        self,
        thickness: float = 2.0,
        color: Optional[Union[str, PaintSource]] = None
    ) -> Self:
        """Adds an underline text decoration.

        Args:
            thickness: The thickness of the underline.
            color: The color of the underline. If `None`, the main text color is used.

        Returns:
            The `Self` instance for chaining.
        """
        decoration_color = self._build_color(color) if color else None
        self._style.underline.set(TextDecoration(
            color=decoration_color,
            thickness=thickness
        ))
        return self

    def strikethrough(
        self,
        thickness: float = 2.0,
        color: Optional[Union[str, PaintSource]] = None
    ) -> Self:
        """Adds a strikethrough text decoration.

        Args:
            thickness: The thickness of the strikethrough line.
            color: The color of the line. If `None`, the main text color is used.

        Returns:
            The `Self` instance for chaining.
        """
        decoration_color = self._build_color(color) if color else None
        self._style.strikethrough.set(TextDecoration(
            color=decoration_color,
            thickness=thickness
        ))
        return self

    @overload
    def padding(self, all: float) -> Self: ...

    @overload
    def padding(self, vertical: float, horizontal: float) -> Self: ...

    @overload
    def padding(
        self, top: float, right: float, bottom: float, left: float
    ) -> Self: ...

    def padding(self, *args: Union[float, int]) -> Self:
        """Sets padding around the element, similar to CSS.

        This method accepts one, two, or four values to specify the padding
        for the top, right, bottom, and left sides.

        Args:
            *args:
                - One value: all four sides.
                - Two values: vertical, horizontal.
                - Four values: top, right, bottom, left.

        Returns:
            The `Self` instance for chaining.

        Raises:
            TypeError: If the number of arguments is not 1, 2, or 4.
        """
        if len(args) == 1:
            value = float(args[0])
            self._style.padding.set((value, value, value, value))
        elif len(args) == 2:
            vertical = float(args[0])
            horizontal = float(args[1])
            self._style.padding.set((vertical, horizontal, vertical, horizontal))
        elif len(args) == 4:
            top, right, bottom, left = map(float, args)
            self._style.padding.set((top, right, bottom, left))
        else:
            raise TypeError(
                f"padding() takes 1, 2, or 4 arguments but got {len(args)}")

        return self

    def background_color(self, color: Union[str, PaintSource]) -> Self:
        """Sets the background color or gradient.

        Args:
            color: A color string or a `PaintSource` object.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.background_color.set(self._build_color(color))
        return self

    # TODO: review this when border gets supported
    def background_radius(self, radius: float) -> Self:
        """Sets the corner radius for the background.

        Args:
            radius: The corner radius value.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.box_radius.set(radius)
        return self

    def text_align(self, alignment: Union[TextAlign, str]) -> Self:
        """Sets the text alignment for multi-line text.

        Args:
            alignment: The alignment, e.g., `Alignment.CENTER` or `"center"`.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.text_align.set(alignment if isinstance(alignment, TextAlign) else TextAlign(alignment))
        return self

    def _build_color(self, color: Union[str, PaintSource]) -> PaintSource:
        """Internal helper to create a SolidColor from a string.

        Args:
            color: The color string or `PaintSource` object.

        Returns:
            A `PaintSource` object.
        """
        return SolidColor.from_str(color) if isinstance(color, str) else color
