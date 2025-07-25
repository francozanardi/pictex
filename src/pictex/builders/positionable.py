from typing import Self, Union, Tuple
from ..models import Position, Style

class PositionableMixin:

    _style: Style

    def position(
            self,
            x: Union[float, int, str],
            y: Union[float, int, str],
            x_offset: float = 0,
            y_offset: float = 0
    ) -> Self:
        """Sets the fixed position of the element using a flexible coordinate system.

        This method defines the element's `x` and `y` coordinates. Each coordinate
        can be specified independently using one of three modes:

        - **Absolute (pixels)**: An `int` or `float` value that sets the
          position directly from the top-left corner.
            `position(100, 250)`

        - **Percentage**: A `str` ending with `%` that sets the position
          relative to the parent container's dimensions.
            `position("50%", "100%")`

        - **Keyword Alignment**: A `str` keyword to align the element.
          Valid keywords for `x` are "left", "center", "right".
          Valid keywords for `y` are "top", "center", "bottom".
            `position("center", "top")`

        These modes can be mixed, for example: `position(100, "center")`.
        Additionally, optional offsets can be applied for fine-tuning.

        Args:
            x (Union[float, int, str]): The horizontal position value. Can be an
                absolute pixel value, a percentage string (e.g., "50%"), or an
                alignment keyword ("left", "center", "right").
            y (Union[float, int, str]): The vertical position value. Can be an
                absolute pixel value, a percentage string (e.g., "75%"), or an
                alignment keyword ("top", "center", "bottom").
            x_offset (float, optional): Apply an
                additional horizontal offset in pixels. Defaults to 0.
            y_offset (float, optional): Apply an
                additional vertical offset in pixels. Defaults to 0.

        Returns:
            Self: The instance for chaining.

        Raises:
            ValueError: If an invalid keyword is used for `x` or `y` (e.g.,
                `position("top", "left")`).
            TypeError: If `x` or `y` are of an unsupported type.
        """
        container_ax, content_ax = self._parse_anchor(x, axis='x')
        container_ay, content_ay = self._parse_anchor(y, axis='y')

        self._style.position.set(Position(
            container_anchor_x=container_ax,
            content_anchor_x=content_ax,
            x_offset=x_offset,
            container_anchor_y=container_ay,
            content_anchor_y=content_ay,
            y_offset=y_offset
        ))
        return self

    def _parse_anchor(self, value: Union[str, int, float], axis: str) -> Tuple[float, float]:
        if not isinstance(value, str):
            return 0, 0

        if value.endswith('%'):
            container_anchor = float(value.rstrip('%')) / 100
            return container_anchor, 0.0

        keywords = {
            'x': {'left': (0.0, 0.0), 'center': (0.5, 0.5), 'right': (1.0, 1.0)},
            'y': {'top': (0.0, 0.0), 'center': (0.5, 0.5), 'bottom': (1.0, 1.0)}
        }

        if value in keywords[axis]:
            return keywords[axis][value]

        raise ValueError(f"Invalid keyword '{value}' for axis '{axis}'")
