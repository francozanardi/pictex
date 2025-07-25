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
    container_anchor_x: float = 0.0
    container_anchor_y: float = 0.0

    content_anchor_x: float = 0.0
    content_anchor_y: float = 0.0

    x_offset: float = 0.0
    y_offset: float = 0.0

    def get_absolute_position(self, content_width: int, content_height: int, container_width: int, container_height: int) -> Tuple[float, float]:
        container_point_x = container_width * self.container_anchor_x
        container_point_y = container_height * self.container_anchor_y

        content_offset_x = content_width * self.content_anchor_x
        content_offset_y = content_height * self.content_anchor_y

        final_x = container_point_x - content_offset_x + self.x_offset
        final_y = container_point_y - content_offset_y + self.y_offset

        return final_x, final_y
