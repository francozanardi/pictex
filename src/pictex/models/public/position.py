from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class VerticalPosition(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"

class HorizontalPosition(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

@dataclass
class Position:
    horizontal: HorizontalPosition = HorizontalPosition.LEFT
    vertical: VerticalPosition = VerticalPosition.TOP
    x_offset: float = 0
    y_offset: float = 0

    def get_absolute_position(self, content_width: int, content_height: int, container_width: int, container_height: int) -> Tuple[float, float]:
        x = self.x_offset
        y = self.y_offset
        if self.horizontal == HorizontalPosition.CENTER:
            x += (container_width / 2.0) - (content_width / 2.0)
        elif self.horizontal == HorizontalPosition.RIGHT:
            x += container_width - content_width

        if self.vertical == VerticalPosition.CENTER:
            y += (container_height / 2.0) - (content_height / 2.0)
        elif self.vertical == VerticalPosition.BOTTOM:
            y += container_height - content_height

        return x, y
