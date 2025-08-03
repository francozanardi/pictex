from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
from .paint_source import PaintSource
from .color import SolidColor
import skia

class BorderStyle(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"

@dataclass
class Border:
    width: float = 1.0
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0))
    style: BorderStyle = BorderStyle.SOLID

@dataclass
class BorderRadiusValue:
    value: float = 0
    mode: Literal['absolute', 'percent'] = 'absolute'

@dataclass
class BorderRadius:
    top_left: BorderRadiusValue
    top_right: BorderRadiusValue
    bottom_right: BorderRadiusValue
    bottom_left: BorderRadiusValue

    def has_any_radius(self) -> bool:
        return any(r.value > 0 for r in [self.top_left, self.top_right, self.bottom_right, self.bottom_left])

    def apply_corner_radius(self, rect: skia.Rect, radius_offset: float = 0) -> skia.RRect:
        rounded_rect = skia.RRect()
        radii_tuples = self.get_absolute_radii(
            rect.width(),
            rect.height()
        )
        adjusted_radii_tuples = [
            (max(0, rx - radius_offset), max(0, ry - radius_offset))
            for rx, ry in radii_tuples
        ]

        rounded_rect.setRectRadii(rect, adjusted_radii_tuples)
        return rounded_rect

    def get_absolute_radii(self, box_width: float, box_height: float) -> list[tuple[float, float]]:
        radii = []
        for corner_value in [self.top_left, self.top_right, self.bottom_right, self.bottom_left]:
            if corner_value.mode == 'percent':
                rx = box_width * (corner_value.value / 100.0)
                ry = box_height * (corner_value.value / 100.0)
                radii.append((rx, ry))
            else: # absolute
                radii.append((corner_value.value, corner_value.value))
        return radii
