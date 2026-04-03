from __future__ import annotations
from typing import Optional, Union, overload, Literal
from pathlib import Path
from ..models import *
from .inline_styleable import InlineStyleable

try:
    from typing import Self # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self

TextBoxEdgeInput = Union[TextBoxEdgeValue, Literal["font", "glyphs"]]

class Stylable(InlineStyleable):

    def line_height(self, value: Union[float, Literal["auto"], LineHeight]) -> Self:
        """Sets the line height.

        Controls the vertical space each line of text occupies.

        Args:
            value: Accepts three forms:

                - **float**: unitless multiplier applied to the current
                  ``font_size``. A value of ``1.5`` on a 20 px font yields
                  30 px per line. Common values: ``1.0`` (tight), ``1.2``
                  (headings), ``1.4``-``1.6`` (comfortable reading).
                - ``"auto"``: restores the default behaviour: each line
                  height is derived from the font's own metrics
                  (``ascent + descent + leading``), similar to CSS
                  ``line-height: normal``.
                - ``LineHeight``: a pre-built instance.

        Returns:
            The ``Self`` instance for chaining.

        Example:
            ```python
            Text("Hello").font_size(20).line_height(1.5)
            # Each line takes 30 px of vertical space.

            Text("Hello").line_height("auto")
            # Restores font-metrics-based line height.
            ```
        """
        if isinstance(value, LineHeight):
            self._style.line_height.set(value)
        elif value == "auto":
            self._style.line_height.set(LineHeight.auto())
        else:
            self._style.line_height.set(LineHeight.multiplier(float(value)))
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
            ```python
            Text("مرحبا").direction("rtl")
            Column(
                Text("Text 1"),  # inherits RTL
                Text("Text 2")   # inherits RTL
            ).direction("rtl")
            ```
        """
        self._style.direction.set(value if isinstance(value, TextDirection) else TextDirection(value))
        return self

    @overload
    def text_box_edge(self, both: TextBoxEdgeInput) -> Self: ...

    @overload
    def text_box_edge(self, *, top: TextBoxEdgeInput = ..., bottom: TextBoxEdgeInput = ...) -> Self: ...

    def text_box_edge(  # type: ignore[misc]
        self,
        both: Optional[TextBoxEdgeInput] = None,
        *,
        top: Optional[TextBoxEdgeInput] = None,
        bottom: Optional[TextBoxEdgeInput] = None,
    ) -> Self:
        """Controls how the top and bottom edges of a text node's box are calculated.

        By default, PicTex uses font metrics (ascent/descent) to size text boxes.
        This produces stable, predictable layouts because the box size depends only
        on the font, ignoring the specific characters in the string.

        This method lets you override that behavior per-edge. It is **inherited**,
        so setting it on a ``Canvas`` or layout container applies to all ``Text``
        nodes inside.

        **Note:**
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
                Defaults to ``"font"`` when omitted.
            bottom: Edge mode for the bottom of the box (keyword-only).
                Defaults to ``"font"`` when omitted.

        Returns:
            The ``Self`` instance for chaining.

        Raises:
            TypeError: If neither ``both`` nor at least one of ``top``/``bottom``
                are provided, or if ``both`` is mixed with ``top``/``bottom``.

        Example:
            Trim both edges to the glyph ink bounds:
            ```python
            Text("Hello").text_box_edge(TextBoxEdgeValue.GLYPHS)
            Text("Hello").text_box_edge("glyphs")
            ```

            Trim only the top edge, keep font metrics at the bottom:
            ```python
            Text("Hello").text_box_edge(top="glyphs")
            Text("Hello").text_box_edge(top="glyphs", bottom="font")  # equivalent
            ```

            Inherit the setting for all Text nodes in a canvas:
            ```python
            Canvas().text_box_edge("glyphs").render("Hello, World!")
            ```
        """
        def _parse(value: Union[TextBoxEdgeValue, str]) -> TextBoxEdgeValue:
            return value if isinstance(value, TextBoxEdgeValue) else TextBoxEdgeValue(value)

        if both is not None and (top is not None or bottom is not None):
            raise TypeError("text_box_edge() does not accept both positional and keyword arguments")

        if both is not None:
            val = _parse(both)
            self._style.text_box_edge.set(TextBoxEdge(top=val, bottom=val))
        elif top is not None or bottom is not None:
            top_val = _parse(top) if top is not None else TextBoxEdgeValue.FONT
            bottom_val = _parse(bottom) if bottom is not None else TextBoxEdgeValue.FONT
            self._style.text_box_edge.set(TextBoxEdge(top=top_val, bottom=bottom_val))
        else:
            raise TypeError("text_box_edge() requires either 'both' or at least one of 'top'/'bottom'")

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

    def padding_top(self, value: Union[float, int]) -> Self:
        """Sets the top padding, preserving the other three sides."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(float(value), p.right, p.bottom, p.left))
        return self

    def padding_right(self, value: Union[float, int]) -> Self:
        """Sets the right padding, preserving the other three sides."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(p.top, float(value), p.bottom, p.left))
        return self

    def padding_bottom(self, value: Union[float, int]) -> Self:
        """Sets the bottom padding, preserving the other three sides."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(p.top, p.right, float(value), p.left))
        return self

    def padding_left(self, value: Union[float, int]) -> Self:
        """Sets the left padding, preserving the other three sides."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(p.top, p.right, p.bottom, float(value)))
        return self

    def padding_horizontal(self, value: Union[float, int]) -> Self:
        """Sets left and right padding equally, preserving top and bottom."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(p.top, float(value), p.bottom, float(value)))
        return self

    def padding_vertical(self, value: Union[float, int]) -> Self:
        """Sets top and bottom padding equally, preserving left and right."""
        p = self._style.padding.get()
        self._style.padding.set(Padding(float(value), p.right, float(value), p.left))
        return self

    def margin_top(self, value: Union[float, int]) -> Self:
        """Sets the top margin, preserving the other three sides."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(float(value), m.right, m.bottom, m.left))
        return self

    def margin_right(self, value: Union[float, int]) -> Self:
        """Sets the right margin, preserving the other three sides."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(m.top, float(value), m.bottom, m.left))
        return self

    def margin_bottom(self, value: Union[float, int]) -> Self:
        """Sets the bottom margin, preserving the other three sides."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(m.top, m.right, float(value), m.left))
        return self

    def margin_left(self, value: Union[float, int]) -> Self:
        """Sets the left margin, preserving the other three sides."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(m.top, m.right, m.bottom, float(value)))
        return self

    def margin_horizontal(self, value: Union[float, int]) -> Self:
        """Sets left and right margin equally, preserving top and bottom."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(m.top, float(value), m.bottom, float(value)))
        return self

    def margin_vertical(self, value: Union[float, int]) -> Self:
        """Sets top and bottom margin equally, preserving left and right."""
        m = self._style.margin.get()
        self._style.margin.set(Margin(float(value), m.right, float(value), m.left))
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
        path: Union[str, Path],
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
            BackgroundImage(path=str(path), size_mode=size_mode)
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
            ```python
            Row(
                Text("Fixed").size(width=100),
                Text("Grows x1").flex_grow(1),
                Text("Grows x2").flex_grow(2)
            )
            ```
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
            ```python
            Row(
                Text("Don't shrink").flex_shrink(0),
                Text("Can shrink").flex_shrink(1)
            )
            ```
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
            ```python
            Row(
                Text("A"),
                Text("B").align_self('end'),  # This one aligns differently
                Text("C")
            ).align_items('start')
            ```
        """
        self._style.align_self.set(alignment if isinstance(alignment, AlignSelf) else AlignSelf(alignment))
        return self

    def overflow(self, value: Union[Overflow, Literal["hidden", "visible"]]) -> Self:
        """Controls how content that exceeds the element's bounds is rendered.

        Equivalent to CSS ``overflow``. When set to ``"hidden"``, any content
        (text, child nodes, images) that extends beyond the element's
        **padding box** is clipped and hidden. The background and border are
        not affected by the clip.

        This property is **not inherited**.

        Args:
            value: ``"hidden"`` to clip overflowing content, or ``"visible"``
                to leave it unclipped (the default). Accepts the ``Overflow``
                enum or its string equivalents.

        Returns:
            The ``Self`` instance for chaining.

        Example:
            ```python
            # Clip text that overflows a fixed-size box:
            Text("Very long text…").size(width=200, height=50).overflow("hidden")

            # Clip children that grow beyond a container:
            Row(child1, child2).size(width=300).overflow("hidden")
            ```
        """
        self._style.overflow.set(
            value if isinstance(value, Overflow) else Overflow(value)
        )
        return self

    def _parse_radius_value(self, value: Union[float, int, str]) -> BorderRadiusValue:
        if isinstance(value, str) and value.endswith('%'):
            return BorderRadiusValue(value=float(value.rstrip('%')), mode='percent')
        elif isinstance(value, (int, float)):
            return BorderRadiusValue(value=float(value), mode='absolute')
        raise TypeError(f"Unsupported type for radius: {type(value).__name__}")
