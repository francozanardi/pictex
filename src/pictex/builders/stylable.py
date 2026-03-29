from __future__ import annotations
from typing import Optional, Union, overload, Literal
from pathlib import Path
from ..models import *

try:
    from typing import Self # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self

TextBoxEdgeArg = Union[TextBoxEdgeValue, Literal["font", "glyphs"]]

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

    def font_weight(self, weight: Union[FontWeight, int, str]) -> Self:
        """Sets the font weight.

        Args:
            weight: The font weight, e.g., `FontWeight.BOLD`, `700` or `"bold"`.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(weight, str):
            try:
                name = weight.upper().replace("-", "_")
                weight = FontWeight[name]
            except KeyError:
                raise ValueError(f"Invalid font weight: {weight}")

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
        """Sets the line height as a unitless multiplier of the font size.

        Controls the vertical space each line of text occupies.  The
        multiplier is applied to the current ``font_size``, so a value of
        ``1.5`` on a 20 px font yields 30 px per line.

        When **not** called, the default behaviour is ``"auto"``: each line
        height is derived from the font's own metrics
        (``ascent + descent + leading``), which is similar to CSS
        ``line-height: normal``.

        Args:
            multiplier: Unitless multiplier applied to the current
                ``font_size``.  Common values:

                - ``1.0``: single spacing (lines packed to exactly
                  ``font_size`` pixels, may feel tight).
                - ``1.2``: compact, often used for headings.
                - ``1.4`` - ``1.6``: comfortable reading spacing.

        Returns:
            The ``Self`` instance for chaining.

        Example::

            Text("Hello").font_size(20).line_height(1.5)
            # Each line takes 30 px of vertical space.
        """
        self._style.line_height.set(LineHeight.from_multiplier(multiplier))
        return self

    def color(self, color: Union[str, PaintSource]) -> Self:
        """Sets the text color or gradient.

        Args:
            color: A color string (e.g., "red", "#FF0000") or a `PaintSource` object.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.color.set(self._build_color(color))
        return self

    def text_shadows(self, *shadows: Shadow) -> Self:
        """Sets the shadow effects for the text. This style is inherited.

        This method applies one or more shadows to the text, replacing any
        previously set text shadows.

        Args:
            *shadows: A sequence of one or more `Shadow` objects to be
                applied to the text.

        Returns:
            The `Self` instance for method chaining.
        """
        self._style.text_shadows.set(list(shadows))
        return self

    def box_shadows(self, *shadows: Shadow) -> Self:
        """Sets the shadow effects for the element box. This style is not inherited.

        This method applies one or more shadows to the box, replacing any
        previously set box shadows.

        Args:
            *shadows: A sequence of one or more `Shadow` objects to be
                applied to the box.

        Returns:
            The `Self` instance for method chaining.
        """
        self._style.box_shadows.set(list(shadows))
        return self

    def text_stroke(
        self, 
        width: float, 
        color: Union[str, PaintSource],
        mode: Union[str, StrokeMode] = "center"
    ) -> Self:
        """Adds a stroke to the text.
        
        By default, follows CSS standards where the stroke is centered on the text path
        (half inside, half outside). You can change this behavior with the mode parameter.
        
        Args:
            width: The width of the stroke in pixels.
            color: The color of the stroke.
            mode: The stroke rendering mode:
                - "center" (default): CSS-compliant centered stroke
                - "outline": Pure outline (stroke only outside the text)
                - "inline": Pure inline (stroke only inside the text)
        
        Returns:
            The `Self` instance for chaining.
        """
        stroke_mode = StrokeMode(mode) if isinstance(mode, str) else mode
        self._style.text_stroke.set(
            OutlineStroke(width=width, color=self._build_color(color), mode=stroke_mode)
        )
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
    def padding(self, all: Union[float, int]) -> Self: ...

    @overload
    def padding(self, vertical: Union[float, int], horizontal: Union[float, int]) -> Self: ...

    @overload
    def padding(
        self, top: Union[float, int], right: Union[float, int], bottom: Union[float, int], left: Union[float, int]
    ) -> Self: ...

    def padding(self, *args: Union[float, int]) -> Self:  # type: ignore[misc]
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
    def margin(self, all: Union[float, int]) -> Self: ...

    @overload
    def margin(self, vertical: Union[float, int], horizontal: Union[float, int]) -> Self: ...

    @overload
    def margin(
        self, top: Union[float, int], right: Union[float, int], bottom: Union[float, int], left: Union[float, int]
    ) -> Self: ...

    def margin(self, *args: Union[float, int]) -> Self:  # type: ignore[misc]
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

    def border_radius(self, *args: Union[float, str]) -> Self:  # type: ignore[misc]
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

    def text_wrap(self, wrap: Union[TextWrap, str]) -> Self:
        """Sets how text should wrap within its container.

        Args:
            wrap: The wrapping behavior, e.g., `TextWrap.NORMAL` or `"normal"` (allow wrapping),
                  or `TextWrap.NOWRAP` or `"nowrap"` (prevent wrapping).

        Returns:
            The `Self` instance for chaining.
        """
        self._style.text_wrap.set(wrap if isinstance(wrap, TextWrap) else TextWrap(wrap))
        return self

    def direction(self, value: Union[TextDirection, Literal["ltr", "rtl"]]) -> Self:
        """Sets the text direction (horizontal flow).
        
        BiDi algorithm runs automatically regardless of this setting.
        This property is inherited by child elements.

        Args:
            value: The text direction, either "ltr" (left-to-right) or "rtl" (right-to-left).
                   Can be a TextDirection enum or a string.

        Returns:
            The `Self` instance for chaining.
        
        Example:
            >>> Text("مرحبا").direction("rtl")
            >>> Column(
            ...     Text("Text 1"),  # inherits RTL
            ...     Text("Text 2")   # inherits RTL
            ... ).direction("rtl")
        """
        self._style.direction.set(value if isinstance(value, TextDirection) else TextDirection(value))
        return self

    @overload
    def text_box_edge(self, both: TextBoxEdgeArg) -> Self: ...

    @overload
    def text_box_edge(self, *, top: TextBoxEdgeArg, bottom: TextBoxEdgeArg) -> Self: ...

    def text_box_edge(  # type: ignore[misc]
        self,
        both: Optional[Union[TextBoxEdgeValue, str]] = None,
        *,
        top: Optional[Union[TextBoxEdgeValue, str]] = None,
        bottom: Optional[Union[TextBoxEdgeValue, str]] = None,
    ) -> Self:
        """Controls how the top and bottom edges of a text node's box are calculated.

        By default, PicTex uses font metrics (ascent/descent) to size text boxes.
        This produces stable, predictable layouts because the box size depends only
        on the font, ignoring the specific characters in the string.

        This method lets you override that behavior per-edge. It is **inherited**,
        so setting it on a ``Canvas`` or layout container applies to all ``Text``
        nodes inside.

        .. note::
            This property is inspired by the CSS ``text-box-trim`` and
            ``text-box-edge`` properties, but does not implement them exactly.

        Edge values:

        - ``"font"`` *(default)*: The edge is placed at the font's ascent (top)
          or descent (bottom). The box always has the same height for a given font
          and size, regardless of content. Safe for dynamic / user-supplied text.
        - ``"glyphs"``: The edge is placed at the actual ink bounds of the rendered
          glyphs. The box tightly wraps the visible characters, removing the empty
          space reserved by the font for ascenders/descenders that are not present.
          **Caution:** the box size becomes content-dependent, so different strings
          produce different heights, which can shift your layout unexpectedly.

        Args:
            both: Applies the same edge mode to both top and bottom.
            top: Edge mode for the top of the box (keyword-only).
            bottom: Edge mode for the bottom of the box (keyword-only).

        Returns:
            The ``Self`` instance for chaining.

        Raises:
            TypeError: If neither ``both`` nor ``top``/``bottom`` are provided,
                or if ``both`` is mixed with ``top``/``bottom``.

        Examples:
            Trim both edges to the glyph ink bounds::

                Text("Hello").text_box_edge(TextBoxEdgeValue.GLYPHS)
                Text("Hello").text_box_edge("glyphs")

            Trim only the top edge, keep font metrics at the bottom::

                Text("Hello").text_box_edge(top="glyphs", bottom="font")

            Inherit the setting for all Text nodes in a canvas::

                Canvas().text_box_edge("glyphs").render("Hello, World!")
        """
        def _parse(value: Union[TextBoxEdgeValue, str]) -> TextBoxEdgeValue:
            return value if isinstance(value, TextBoxEdgeValue) else TextBoxEdgeValue(value)

        if both is not None and (top is not None or bottom is not None):
            raise TypeError("text_box_edge() does not accept both positional and keyword arguments")

        if both is not None:
            val = _parse(both)
            self._style.text_box_edge.set(TextBoxEdge(top=val, bottom=val))
        elif top is not None and bottom is not None:
            self._style.text_box_edge.set(TextBoxEdge(top=_parse(top), bottom=_parse(bottom)))
        else:
            raise TypeError("text_box_edge() requires either 'both' or both 'top' and 'bottom'")

        return self

    def flex_grow(self, value: float) -> Self:
        """Sets the flex grow factor for this element (CSS flex-grow).
        
        Controls how much this element should grow relative to siblings when
        there's extra space in the flex container.
        
        Args:
            value: The grow factor. 0 means no growth (default), 1+ means grow.
                   Higher values grow proportionally more.
        
        Returns:
            The `Self` instance for chaining.
        
        Example:
            >>> Row(
            ...     Text("Fixed").size(width=100),
            ...     Text("Grows x1").flex_grow(1),
            ...     Text("Grows x2").flex_grow(2)
            ... )
        """
        self._style.flex_grow.set(float(value))
        return self

    def flex_shrink(self, value: float) -> Self:
        """Sets the flex shrink factor for this element (CSS flex-shrink).
        
        Controls how much this element should shrink relative to siblings when
        the container is too small.
        
        Args:
            value: The shrink factor. 0 means no shrinking, 1 means shrink
                   proportionally (default). Higher values shrink more.
        
        Returns:
            The `Self` instance for chaining.
        
        Example:
            >>> Row(
            ...     Text("Don't shrink").flex_shrink(0),
            ...     Text("Can shrink").flex_shrink(1)
            ... )
        """
        self._style.flex_shrink.set(float(value))
        return self

    def align_self(self, alignment: Union[AlignSelf, str]) -> Self:
        """Override the container's align-items for this specific element (CSS align-self).
        
        Allows an individual flex item to override the alignment set by its container.
        
        Args:
            alignment: Alignment mode. Can be 'auto', 'start', 'center', 'end', or 'stretch'.
                      'auto' uses the container's align-items value (default).
        
        Returns:
            The `Self` instance for chaining.
        
        Example:
            >>> Row(
            ...     Text("A"),
            ...     Text("B").align_self('end'),  # This one aligns differently
            ...     Text("C")
            ... ).align_items('start')
        """
        self._style.align_self.set(alignment if isinstance(alignment, AlignSelf) else AlignSelf(alignment))
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
