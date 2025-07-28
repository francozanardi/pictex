from __future__ import annotations
from typing import Optional, Union, overload, Self, Literal
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
            self._style.padding.set(Padding(value, value, value, value))
        elif len(args) == 2:
            vertical = float(args[0])
            horizontal = float(args[1])
            self._style.padding.set(Padding(vertical, horizontal, vertical, horizontal))
        elif len(args) == 4:
            top, right, bottom, left = map(float, args)
            self._style.padding.set(Padding(top, right, bottom, left))
        else:
            raise TypeError(
                f"padding() takes 1, 2, or 4 arguments but got {len(args)}")

        return self

    @overload
    def margin(self, all: float) -> Self: ...

    @overload
    def margin(self, vertical: float, horizontal: float) -> Self: ...

    @overload
    def margin(
        self, top: float, right: float, bottom: float, left: float
    ) -> Self: ...

    def margin(self, *args: Union[float, int]) -> Self:
        """Sets margin around the element, similar to CSS.

        This method accepts one, two, or four values to specify the margin
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
            self._style.margin.set(Margin(value, value, value, value))
        elif len(args) == 2:
            vertical = float(args[0])
            horizontal = float(args[1])
            self._style.margin.set(Margin(vertical, horizontal, vertical, horizontal))
        elif len(args) == 4:
            top, right, bottom, left = map(float, args)
            self._style.margin.set(Margin(top, right, bottom, left))
        else:
            raise TypeError(
                f"margin() takes 1, 2, or 4 arguments but got {len(args)}")

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

    def background_image(
        self,
        path: str,
        size_mode: Union[BackgroundImageSizeMode, Literal["cover", "contain", "tile"]] = BackgroundImageSizeMode.COVER
    ) -> Self:
        """Sets a background image for the element.

        Args:
            path (str): The path to the image file.
            size_mode (Union[BackgroundImageSizeMode, str]): The fitting strategy.
                Can be 'cover', 'contain', or 'tile'.
                - 'cover': The image is resized to completely cover the element's box,
                  maintaining its aspect ratio. The image may be cropped.
                - 'contain': The image is resized to fit entirely within the box,
                  maintaining its aspect ratio. This may leave empty space.
                - 'tile': The image is tiled at its original size without resizing.

        Returns:
            Self: The instance for method chaining.
        """
        if isinstance(size_mode, str):
            size_mode = BackgroundImageSizeMode(size_mode.lower())

        self._style.background_image.set(
            BackgroundImage(path=path, size_mode=size_mode)
        )
        return self

    def border(
        self,
        width: float,
        color: Union[str, PaintSource],
        style: Union[str, BorderStyle] = BorderStyle.SOLID
    ) -> Self:
        """
        Sets the border for the element.

        Args:
            width: The width of the border in pixels.
            color: The color of the border (e.g., "red", "#FF0000") or a PaintSource object.
            style: The style of the borderline. Can be 'solid', 'dashed', or 'dotted'.

        Returns:
            The `Self` instance for method chaining.
        """
        border_color = self._build_color(color)
        if isinstance(style, str):
            style = BorderStyle(style.lower())

        self._style.border.set(
            Border(width=width, color=border_color, style=style)
        )
        return self

    @overload
    def border_radius(self, all: Union[float, str]) -> Self: ...
    @overload
    def border_radius(self, top_bottom: Union[float, str], left_right: Union[float, str]) -> Self: ...
    @overload
    def border_radius(self, top_left: Union[float, str], top_right: Union[float, str], bottom_right: Union[float, str], bottom_left: Union[float, str]) -> Self: ...

    def border_radius(self, *args: Union[float, str]) -> Self:
        """
        Sets the corner radius for the background, similar to CSS border-radius.
        Accepts absolute values (pixels) or percentages as strings (e.g., "50%").

        Args:
            *args:
                - One value: all four corners.
                - Two values: [top-left, bottom-right], [top-right, bottom-left].
                - Four values: [top-left], [top-right], [bottom-right], [bottom-left].

        Returns:
            The `Self` instance for chaining.
        """
        if len(args) == 1:
            val = self._parse_radius_value(args[0])
            self._style.border_radius.set(BorderRadius(val, val, val, val))
        elif len(args) == 2:
            val1 = self._parse_radius_value(args[0])
            val2 = self._parse_radius_value(args[1])
            self._style.border_radius.set(BorderRadius(val1, val2, val1, val2))
        elif len(args) == 4:
            tl, tr, br, bl = map(self._parse_radius_value, args)
            self._style.border_radius.set(BorderRadius(tl, tr, br, bl))
        else:
            raise TypeError(f"border_radius() takes 1, 2, or 4 arguments but got {len(args)}")

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

    def _parse_radius_value(self, value: Union[float, int, str]) -> BorderRadiusValue:
        if isinstance(value, str) and value.endswith('%'):
            return BorderRadiusValue(value=float(value.rstrip('%')), mode='percent')
        elif isinstance(value, (int, float)):
            return BorderRadiusValue(value=float(value), mode='absolute')
        raise TypeError(f"Unsupported type for radius: {type(value).__name__}")
