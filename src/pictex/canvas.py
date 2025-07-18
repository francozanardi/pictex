from __future__ import annotations
from typing import Optional, Union, overload
from pathlib import Path
from .models import *
from .image import Image
from .vector_image import VectorImage
from .renderer import Renderer

class Canvas:
    """The main user-facing class for creating stylized text images.

    This class implements a fluent builder pattern to define a style template,
    which can then be used to render multiple texts. Each styling method returns
    the instance of the class, allowing for method chaining.

    Example:
        ```python
        canvas = Canvas()
        image = (
            canvas.font_family("Arial")
            .font_size(24)
            .color("blue")
            .add_shadow(offset=(2, 2), blur_radius=3, color="black")
            .render("Hello, World!")
        )
        image.save("output.png")
        ```
    """

    def __init__(self, style: Optional[Style] = None):
        """Initializes a new Canvas with an optional base style.

        Args:
            style: An optional base `Style` object to initialize the canvas with.
                If not provided, a default style is created.
        """
        self._style = style if style is not None else Style()

    def font_family(self, family: Union[str, Path]) -> Canvas:
        """Sets the font family or a path to a font file.

        Args:
            family: The name of the font family or a `Path` object to a font file.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.family = str(family)
        return self

    def font_fallbacks(self, *fonts: Union[str, Path]) -> Canvas:
        """Specifies a list of fallback fonts.

        These fonts are used for characters not supported by the primary font.

        Args:
            *fonts: A sequence of font names or `Path` objects to font files.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font_fallbacks = [str(font) for font in fonts]
        return self

    def font_size(self, size: float) -> Canvas:
        """Sets the font size in points.

        Args:
            size: The new font size.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.size = size
        return self

    def font_weight(self, weight: Union[FontWeight, int]) -> Canvas:
        """Sets the font weight.

        Args:
            weight: The font weight, e.g., `FontWeight.BOLD` or `700`.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.weight = weight if isinstance(
            weight, FontWeight) else FontWeight(weight)
        return self

    def font_style(self, style: Union[FontStyle, str]) -> Canvas:
        """Sets the font style.

        Args:
            style: The font style, e.g., `FontStyle.ITALIC`.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.style = style if isinstance(
            style, FontStyle) else FontStyle(style)
        return self

    def color(self, color: Union[str, PaintSource]) -> Canvas:
        """Sets the primary text color or gradient.

        Args:
            color: A color string (e.g., "red", "#FF0000") or a `PaintSource` object.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.color = self.__build_color(color)
        return self

    def add_shadow(
        self,
        offset: tuple[float, float],
        blur_radius: float = 0,
        color: Union[str, SolidColor] = 'black'
    ) -> Canvas:
        """Adds a text shadow effect.

        This method can be called multiple times to add multiple shadows.

        Args:
            offset: A tuple `(dx, dy)` for the shadow's offset.
            blur_radius: The blur radius of the shadow.
            color: The color of the shadow.

        Returns:
            The `Canvas` instance for chaining.
        """
        shadow_color = self.__build_color(color)
        self._style.shadows.append(Shadow(offset, blur_radius, shadow_color))
        return self

    def add_box_shadow(
        self,
        offset: tuple[float, float],
        blur_radius: float = 0,
        color: Union[str, SolidColor] = 'black'
    ) -> Canvas:
        """Adds a background box shadow.

        This method can be called multiple times to add multiple shadows.

        Args:
            offset: A tuple `(dx, dy)` for the shadow's offset.
            blur_radius: The blur radius of the shadow.
            color: The color of the shadow.

        Returns:
            The `Canvas` instance for chaining.
        """
        shadow_color = self.__build_color(color)
        self._style.box_shadows.append(
            Shadow(offset, blur_radius, shadow_color))
        return self

    def outline_stroke(self, width: float, color: Union[str, PaintSource]) -> Canvas:
        """Adds an outline stroke to the text.

        Args:
            width: The width of the outline stroke.
            color: The color of the outline.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.outline_stroke = OutlineStroke(
            width=width, color=self.__build_color(color))
        return self

    def underline(
        self,
        thickness: float = 2.0,
        color: Optional[Union[str, PaintSource]] = None
    ) -> Canvas:
        """Adds an underline text decoration.

        Args:
            thickness: The thickness of the underline.
            color: The color of the underline. If `None`, the main text color is used.

        Returns:
            The `Canvas` instance for chaining.
        """
        decoration_color = self.__build_color(color) if color else None
        self._style.decorations.append(
            TextDecoration(
                line=DecorationLine.UNDERLINE,
                color=decoration_color,
                thickness=thickness
            )
        )
        return self

    def strikethrough(
        self,
        thickness: float = 2.0,
        color: Optional[Union[str, PaintSource]] = None
    ) -> Canvas:
        """Adds a strikethrough text decoration.

        Args:
            thickness: The thickness of the strikethrough line.
            color: The color of the line. If `None`, the main text color is used.

        Returns:
            The `Canvas` instance for chaining.
        """
        decoration_color = self.__build_color(color) if color else None
        self._style.decorations.append(
            TextDecoration(
                line=DecorationLine.STRIKETHROUGH,
                color=decoration_color,
                thickness=thickness
            )
        )
        return self

    @overload
    def padding(self, all: float) -> Canvas: ...

    @overload
    def padding(self, vertical: float, horizontal: float) -> Canvas: ...

    @overload
    def padding(
        self, top: float, right: float, bottom: float, left: float
    ) -> Canvas: ...

    def padding(self, *args: Union[float, int]) -> Canvas:
        """Sets padding around the text, similar to CSS.

        This method accepts one, two, or four values to specify the padding
        for the top, right, bottom, and left sides.

        Args:
            *args:
                - One value: all four sides.
                - Two values: vertical, horizontal.
                - Four values: top, right, bottom, left.

        Returns:
            The `Canvas` instance for chaining.

        Raises:
            TypeError: If the number of arguments is not 1, 2, or 4.
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
            raise TypeError(
                f"padding() takes 1, 2, or 4 arguments but got {len(args)}")

        return self

    def background_color(self, color: Union[str, PaintSource]) -> Canvas:
        """Sets the background color or gradient.

        Args:
            color: A color string or a `PaintSource` object.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.background.color = self.__build_color(color)
        return self

    def background_radius(self, radius: float) -> Canvas:
        """Sets the corner radius for the background.

        Args:
            radius: The corner radius value.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.background.corner_radius = radius
        return self

    def line_height(self, multiplier: float) -> Canvas:
        """Sets the line height as a multiplier of the font size.

        For example, a value of 1.5 corresponds to 150% line spacing.

        Args:
            multiplier: The line height multiplier.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.line_height = multiplier
        return self

    def alignment(self, alignment: Union[Alignment, str]) -> Canvas:
        """Sets the text alignment for multi-line text.

        Args:
            alignment: The alignment, e.g., `Alignment.CENTER` or `"center"`.

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.alignment = alignment if isinstance(
            alignment, Alignment) else Alignment(alignment)
        return self

    def font_smoothing(self, mode: Union[FontSmoothing, str]) -> Canvas:
        """Sets the font antialiasing strategy.

        Args:
            mode: The font smoothing mode. Accepts either `FontSmoothing.SUBPIXEL`
                or `FontSmoothing.STANDARD`, or their string equivalents
                (`"subpixel"` or `"standard"`).

        Returns:
            The `Canvas` instance for chaining.
        """
        self._style.font.smoothing = mode if isinstance(
            mode, FontSmoothing) else FontSmoothing(mode)
        return self

    def render(self, text: str, crop_mode: CropMode = CropMode.NONE) -> Image:
        """Renders an image from the given text using the configured style.

        Args:
            text: The text string to render. Can contain newlines (`\\n`).
            crop_mode: The cropping strategy for the final canvas.
                - `SMART`: Tightly crops to only visible pixels.
                - `CONTENT_BOX`: Crops to the text + padding area.
                - `NONE`: No cropping, includes all effect boundaries (default).

        Returns:
            An `Image` object containing the rendered result.
        """
        renderer = Renderer(self._style)
        return renderer.render_as_bitmap(text, crop_mode)

    def render_as_svg(
        self, text: str, embed_font: bool = True
    ) -> VectorImage:
        """Renders the text as a scalable vector graphic (SVG).

        This method produces a vector-based image, ideal for web use and
        applications requiring resolution independence.

        Args:
            text: The text string to render.
            embed_font: If `True` (default), any custom font files (`.ttf`/`.otf`)
                provided will be embedded directly into the SVG. This
                ensures perfect visual fidelity across all devices but
                increases file size. A warning will be issued if a system
                font is used with this option enabled. If `False`, the SVG will
                reference the font by name, relying on the viewing system to
                have the font installed.

        Returns:
            A `VectorImage` object containing the SVG data.
        """
        renderer = Renderer(self._style)
        return renderer.render_as_svg(text, embed_font)

    def __build_color(self, color: Union[str, PaintSource]) -> PaintSource:
        """Internal helper to create a SolidColor from a string.

        Args:
            color: The color string or `PaintSource` object.

        Returns:
            A `PaintSource` object.
        """
        return SolidColor.from_str(color) if isinstance(color, str) else color