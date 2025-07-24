from typing import overload, Self, Union
from .stylable import Stylable
from ..models import VerticalPosition, HorizontalPosition, Position

# TODO: convert to Mixin and use multiple-inheritance
class StylableWithPosition(Stylable):

    @overload
    def position(self, x: float, y: float) -> Self:
        ...

    @overload
    def position(
            self,
            horizontal: Union[HorizontalPosition, str],
            vertical: Union[VerticalPosition, str],
            x_offset: float = 0,
            y_offset: float = 0
    ) -> Self:
        ...

    def position(self, *args: Union[HorizontalPosition, VerticalPosition, str, float]) -> Self:
        """
        Sets the fixed position of the element.

        This method supports two input modes:

        - **Absolute coordinates**:
            `position(x, y)`
            Directly sets the position using pixel coordinates from the top-left corner.

        - **Relative anchor + offset**:
            `position(horizontal, vertical, x_offset, y_offset)`
            Anchors the element to a reference point (e.g., "center", "top", "bottom-right") and applies an optional offset.

        Args:
            *args:
                - If 2 values are provided: `(x: float, y: float)`
                - If 4 values are provided:
                    - `horizontal` (`HorizontalPosition` or `str`): "left", "center", or "right"
                    - `vertical` (`VerticalPosition` or `str`): "top", "center", or "bottom"
                    - `x_offset` (`float`): Horizontal offset from the anchor point
                    - `y_offset` (`float`): Vertical offset from the anchor point

        Returns:
            Self: The instance for chaining.

        Raises:
            TypeError: If the number of arguments is not 2 or 4.
        """
        if len(args) == 2:
            x = float(args[0])
            y = float(args[1])
            self._style.position = Position(HorizontalPosition.LEFT, VerticalPosition.TOP, x, y)
        elif len(args) == 4:
            horizontal = HorizontalPosition(args[0])
            vertical = VerticalPosition(args[1])
            dx = args[2]
            dy = args[3]
            self._style.position = Position(horizontal, vertical, dx, dy)
        else:
            raise TypeError(
                f"position() takes 2 or 4 arguments but got {len(args)}"
            )

        return self
