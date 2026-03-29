from enum import Enum
from typing import NamedTuple


class LineHeightMode(str, Enum):
    AUTO = "auto"
    """
    The line height is derived entirely from the font's own metrics:
    ``ascent + descent + leading``.
    """

    MULTIPLIER = "multiplier"
    """
    The line height is a unitless multiplier applied to the current
    ``font_size``.  A value of ``1.5`` means each line occupies
    ``1.5 * font_size`` pixels of vertical space, regardless of the
    font's own metrics.  This mirrors the CSS ``line-height: <number>``
    behaviour.
    """


class LineHeight(NamedTuple):
    """
    Resolved line-height value used internally by the rendering pipeline.

    Attributes:
        mode: Whether the height is computed from font metrics (``AUTO``)
            or from an explicit multiplier (``MULTIPLIER``).
        value: The multiplier to use when ``mode`` is ``MULTIPLIER``.
            Ignored when ``mode`` is ``AUTO``.
    """

    mode: LineHeightMode
    value: float = 0.0

    @staticmethod
    def auto() -> "LineHeight":
        """Return an AUTO line-height instance."""
        return LineHeight(mode=LineHeightMode.AUTO)

    @staticmethod
    def multiplier(multiplier: float) -> "LineHeight":
        """Return a MULTIPLIER line-height instance.

        Args:
            multiplier: Unitless multiplier applied to the current
                ``font_size``.  For example, ``1.5`` means 150 % line
                spacing.
        """
        return LineHeight(mode=LineHeightMode.MULTIPLIER, value=multiplier)

    @property
    def is_auto(self) -> bool:
        """``True`` when the mode is :attr:`LineHeightMode.AUTO`."""
        return self.mode == LineHeightMode.AUTO
