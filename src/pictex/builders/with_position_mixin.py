from typing import Union, Optional

try:
    from typing import Self # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self

from ..models import Style, Position, PositionType, Inset, Transform


InsetValue = Optional[Union[float, int, str]]
TranslateValue = Optional[Union[float, int, str]]

class WithPositionMixin:
    """Mixin providing CSS-compliant positioning methods."""

    _style: Style

    def absolute_position(
        self,
        *,
        top: InsetValue = None,
        right: InsetValue = None,
        bottom: InsetValue = None,
        left: InsetValue = None,
    ) -> Self:
        """Position element absolutely (out of normal flow).

        The element is positioned relative to its nearest ancestor.

        Args:
            top: Distance from top edge
            right: Distance from right edge
            bottom: Distance from bottom edge
            left: Distance from left edge

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            Text("Badge").absolute_position(top=10, right=10)
            Text("Footer").absolute_position(bottom=0, left=0, right=0)
            ```
        """
        return self._set_position(PositionType.ABSOLUTE, top, right, bottom, left)

    def fixed_position(
        self,
        *,
        top: InsetValue = None,
        right: InsetValue = None,
        bottom: InsetValue = None,
        left: InsetValue = None,
    ) -> Self:
        """Position element fixed (out of normal flow, relative to canvas).

        The element is always positioned relative to the canvas (viewport),
        regardless of its position in the DOM tree. This is like CSS position: fixed.

        Args:
            top: Distance from canvas top edge
            right: Distance from canvas right edge
            bottom: Distance from canvas bottom edge
            left: Distance from canvas left edge

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            Text("Watermark").fixed_position(bottom=10, right=10)
            Text("Header").fixed_position(top=0, left=0, right=0)
            ```
        """
        return self._set_position(PositionType.FIXED, top, right, bottom, left)

    def relative_position(
        self,
        *,
        top: InsetValue = None,
        right: InsetValue = None,
        bottom: InsetValue = None,
        left: InsetValue = None,
    ) -> Self:
        """Position element relatively (stays in flow, but offset visually).

        The element remains in normal flow but is visually offset by the
        specified values.

        Args:
            top: Offset from normal top position
            right: Offset from normal right position
            bottom: Offset from normal bottom position
            left: Offset from normal left position

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            Text("Nudged").relative_position(top=5, left=5)
            ```
        """
        return self._set_position(PositionType.RELATIVE, top, right, bottom, left)

    def translate(
        self,
        *,
        x: TranslateValue = None,
        y: TranslateValue = None,
    ) -> Self:
        """Apply a translate transform to the element.

        This is applied post-layout as a visual offset. Commonly used with
        absolute_position for true centering.

        Values can be pixels (int/float) or percentages of the element's own
        size (str like "-50%").

        Args:
            x: Horizontal translation
            y: Vertical translation

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            # True centering
            Text("Centered").absolute_position(top="50%", left="50%").translate(x="-50%", y="-50%")
            ```
        """
        self._style.transform.set(Transform(translate_x=x, translate_y=y))
        return self

    def place(
        self,
        horizontal: Union[float, int, str],
        vertical: Union[float, int, str],
        x_offset: float = 0,
        y_offset: float = 0,
    ) -> Self:
        """Place element using anchor-based positioning (canvas-relative).

        This is a convenience method that combines fixed positioning and
        translate to provide intuitive anchor-based placement relative to
        the canvas (viewport).

        Args:
            horizontal: Horizontal anchor - "left", "center", "right", pixels, or "X%"
            vertical: Vertical anchor - "top", "center", "bottom", pixels, or "Y%"
            x_offset: Additional horizontal offset in pixels (default 0)
            y_offset: Additional vertical offset in pixels (default 0)

        Returns:
            Self: The instance for method chaining.

        Example:
            ```python
            Text("Overlay").place("center", "center")
            Text("Badge").place("right", "top", x_offset=-10, y_offset=10)
            ```
        """
        left, right, translate_x = self._parse_horizontal_anchor(horizontal)
        top, bottom, translate_y = self._parse_vertical_anchor(vertical)

        if x_offset != 0:
            translate_x = (translate_x or 0) + x_offset if isinstance(translate_x, (int, float, type(None))) else x_offset
        if y_offset != 0:
            translate_y = (translate_y or 0) + y_offset if isinstance(translate_y, (int, float, type(None))) else y_offset

        self._style.position.set(Position(
            type=PositionType.FIXED,
            inset=Inset(top=top, right=right, bottom=bottom, left=left)
        ))

        if translate_x is not None or translate_y is not None:
            self._style.transform.set(Transform(translate_x=translate_x, translate_y=translate_y))

        return self

    def _set_position(
        self,
        position_type: PositionType,
        top: InsetValue = None,
        right: InsetValue = None,
        bottom: InsetValue = None,
        left: InsetValue = None,
    ) -> Self:
        """Internal method to set position and inset values."""
        self._style.position.set(Position(
            type=position_type,
            inset=Inset(top=top, right=right, bottom=bottom, left=left)
        ))
        return self

    def _parse_horizontal_anchor(self, value: Union[str, int, float]) -> tuple:
        """Parse horizontal anchor to (left, right, translate_x) tuple."""
        if isinstance(value, (int, float)):
            return value, None, None  # left=value

        if value.endswith('%'):
            pct = float(value.rstrip('%'))
            if pct == 0:
                return 0, None, None  # left=0
            elif pct == 100:
                return None, 0, None  # right=0, already positioned correctly
            else:
                return value, None, f"-{pct}%"  # left=X%, translate to center on point

        if value == 'left':
            return 0, None, None
        elif value == 'center':
            return "50%", None, "-50%"
        elif value == 'right':
            return None, 0, None  # right=0, already positioned correctly

        raise ValueError(f"Invalid horizontal anchor value '{value}'")

    def _parse_vertical_anchor(self, value: Union[str, int, float]) -> tuple:
        """Parse vertical anchor to (top, bottom, translate_y) tuple."""
        if isinstance(value, (int, float)):
            return value, None, None  # top=value

        if value.endswith('%'):
            pct = float(value.rstrip('%'))
            if pct == 0:
                return 0, None, None  # top=0
            elif pct == 100:
                return None, 0, None  # bottom=0, already positioned correctly
            else:
                return value, None, f"-{pct}%"  # top=X%, translate to center on point

        if value == 'top':
            return 0, None, None
        elif value == 'center':
            return "50%", None, "-50%"
        elif value == 'bottom':
            return None, 0, None  # bottom=0, already positioned correctly

        raise ValueError(f"Invalid vertical anchor value '{value}'")

