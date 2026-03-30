from __future__ import annotations
from typing import Optional, Union
from pathlib import Path
from ..models import *

try:
    from typing import Self  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self


class InlineStyleable:
    """Mixin exposing only inline/typography style methods.

    Used by builders whose content is purely inline text (e.g. ``Span``).
    Layout properties (padding, margin, border, flex, etc.) are intentionally
    absent - they have no meaning for inline fragments.
    """

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
        """Sets the font style.

        Args:
            style: The font style, e.g., `FontStyle.ITALIC`.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.font_style.set(style if isinstance(style, FontStyle) else FontStyle(style))
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
        """Sets the shadow effects for the text.

        Args:
            *shadows: A sequence of one or more `Shadow` objects.

        Returns:
            The `Self` instance for chaining.
        """
        self._style.text_shadows.set(list(shadows))
        return self

    def text_stroke(
        self,
        width: float,
        color: Union[str, PaintSource],
        mode: Union[str, StrokeMode] = "center"
    ) -> Self:
        """Adds a stroke to the text.

        Args:
            width: The width of the stroke in pixels.
            color: The color of the stroke.
            mode: The stroke rendering mode: "center", "outline", or "inline".

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
        self._style.underline.set(TextDecoration(color=decoration_color, thickness=thickness))
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
        self._style.strikethrough.set(TextDecoration(color=decoration_color, thickness=thickness))
        return self

    def letter_spacing(self, value: Union[float, int, str, LetterSpacing]) -> Self:
        """Sets the extra space between characters (CSS ``letter-spacing``).

        Args:
            value: Absolute pixels (float/int), a percentage string (e.g. ``"10%"``),
                   ``"normal"``, or a ``LetterSpacing`` instance.

        Returns:
            The `Self` instance for chaining.
        """
        if isinstance(value, LetterSpacing):
            self._style.letter_spacing.set(value)
        elif isinstance(value, str):
            if value.strip().lower() == "normal":
                self._style.letter_spacing.set(LetterSpacing.normal())
            elif value.endswith("%"):
                self._style.letter_spacing.set(
                    LetterSpacing.percent(float(value.rstrip("%")))
                )
            else:
                raise ValueError(
                    f"Invalid letter_spacing string: {value!r}. "
                    "Expected a percentage (e.g. '10%') or 'normal'."
                )
        else:
            self._style.letter_spacing.set(LetterSpacing.pixels(float(value)))
        return self

    def _build_color(self, color: Union[str, PaintSource]) -> PaintSource:
        return SolidColor.from_str(color) if isinstance(color, str) else color
