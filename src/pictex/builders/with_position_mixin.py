from typing import Union, Tuple
from ..models import Position, Style, PositionMode

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class WithPositionMixin:

    _style: Style

    def absolute_position(
            self,
            x: Union[float, int, str],
            y: Union[float, int, str],
            x_offset: float = 0,
            y_offset: float = 0
    ) -> Self:
        """Sets the element's position relative to the root canvas.

        This method removes the element from the normal layout flow (`Row` or
        `Column`) and positions it based on the absolute dimensions of the
        entire canvas. The (0, 0) coordinate is the top-left corner of the
        final rendered image, ignoring any margin, border, or padding set on
        the root container.

        This is ideal for global overlays like watermarks or headers that should
        be placed at a fixed position on the final image.

        The coordinate system (`x`, `y`) supports three modes:
        - **Absolute (pixels)**: `absolute_position(100, 250)`
        - **Percentage**: `absolute_position("50%", "100%")`
        - **Keyword Alignment**: `absolute_position("center", "top")`

        Args:
            x (Union[float, int, str]): The horizontal position value. Can be an
                absolute pixel value, a percentage string (e.g., "50%"), or an
                alignment keyword ("left", "center", "right").
            y (Union[float, int, str]): The vertical position value. Can be an
                absolute pixel value, a percentage string (e.g., "75%"), or an
                alignment keyword ("top", "center", "bottom").
            x_offset (float, optional): An additional horizontal offset in
                pixels. Defaults to 0.
            y_offset (float, optional): An additional vertical offset in
                pixels. Defaults to 0.

        Returns:
            Self: The instance for method chaining.
        """
        return self._set_position(x, y, x_offset, y_offset, PositionMode.ABSOLUTE)

    def position(
            self,
            x: Union[float, int, str],
            y: Union[float, int, str],
            x_offset: float = 0,
            y_offset: float = 0
    ) -> Self:
        """Sets the element's position relative to its direct parent's content area.

        This method removes the element from the normal layout flow (`Row` or
        `Column`) and positions it relative to its immediate parent. The (0, 0)
        coordinate is the top-left corner *inside* the parent's padding and
        border. The element will be correctly offset by its parent's position.

        This is ideal for creating overlays within a component, such as placing a
        badge on an image or custom-placing text inside a styled container.

        The coordinate system (`x`, `y`) supports three modes:
        - **Absolute (pixels)**: `position(100, 250)`
        - **Percentage**: `position("50%", "100%")`
        - **Keyword Alignment**: `position("center", "top")`

        Args:
            x (Union[float, int, str]): The horizontal position value. Can be an
                absolute pixel value, a percentage string (e.g., "50%"), or an
                alignment keyword ("left", "center", "right").
            y (Union[float, int, str]): The vertical position value. Can be an
                absolute pixel value, a percentage string (e.g., "75%"), or an
                alignment keyword ("top", "center", "bottom").
            x_offset (float, optional): An additional horizontal offset in
                pixels. Defaults to 0.
            y_offset (float, optional): An additional vertical offset in
                pixels. Defaults to 0.

        Returns:
            Self: The instance for method chaining.
        """
        return self._set_position(x, y, x_offset, y_offset, PositionMode.RELATIVE)

    def _set_position(
            self,
            x: Union[float, int, str],
            y: Union[float, int, str],
            x_offset: float,
            y_offset: float,
            mode: PositionMode
    ) -> Self:
        container_ax, content_ax = self._parse_anchor(x, axis='x')
        container_ay, content_ay = self._parse_anchor(y, axis='y')
        x_offset = x + x_offset if isinstance(x, (float, int)) else x_offset
        y_offset = y + y_offset if isinstance(y, (float, int)) else y_offset

        self._style.position.set(Position(
            container_anchor_x=container_ax,
            content_anchor_x=content_ax,
            x_offset=x_offset,
            container_anchor_y=container_ay,
            content_anchor_y=content_ay,
            y_offset=y_offset,
            mode=mode
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
