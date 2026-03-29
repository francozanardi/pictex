from enum import Enum
from typing import NamedTuple


class LetterSpacingMode(str, Enum):
    NORMAL = "normal"
    """
    The normal letter spacing for the current font.
    """

    ABSOLUTE = "absolute"
    """
    Extra inter-character space (in pixels) added to the default space between
    characters. A negative value reduces the space. Mirrors the CSS
    ``letter-spacing: <length>`` behaviour.
    """

    PERCENT = "percent"
    """
    Extra inter-character space expressed as a percentage of the width of the
    space character of the font applied to the text. Mirrors the CSS
    ``letter-spacing: <percentage>`` behaviour.
    """


class LetterSpacing(NamedTuple):
    """
    Resolved letter-spacing value used internally by the rendering pipeline.

    Attributes:
        mode: Whether the spacing is the font's default (``NORMAL``), an
            explicit pixel offset (``ABSOLUTE``), or a percentage of the
            space-character width (``PERCENT``).
        value: The offset to use when ``mode`` is ``ABSOLUTE`` or ``PERCENT``.
            Ignored when ``mode`` is ``NORMAL``.
    """

    mode: LetterSpacingMode
    value: float = 0.0

    @staticmethod
    def normal() -> "LetterSpacing":
        """Return a NORMAL letter-spacing instance."""
        return LetterSpacing(mode=LetterSpacingMode.NORMAL)

    @staticmethod
    def pixels(pixels: float) -> "LetterSpacing":
        """Return an ABSOLUTE letter-spacing instance.

        Args:
            pixels: Extra space in pixels added between each pair of characters.
                Negative values reduce the default spacing.
        """
        return LetterSpacing(mode=LetterSpacingMode.ABSOLUTE, value=pixels)

    @staticmethod
    def percent(percent: float) -> "LetterSpacing":
        """Return a PERCENT letter-spacing instance.

        Args:
            percent: Extra space expressed as a percentage of the space-character
                width of the current font. E.g. ``10`` means 10 %.
        """
        return LetterSpacing(mode=LetterSpacingMode.PERCENT, value=percent)

    @property
    def is_normal(self) -> bool:
        """``True`` when the mode is :attr:`LetterSpacingMode.NORMAL`."""
        return self.mode == LetterSpacingMode.NORMAL
