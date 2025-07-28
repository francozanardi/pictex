from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Literal
import skia

class BackgroundImageSizeMode(str, Enum):
    COVER = "cover"
    CONTAIN = "contain"
    TILE = "tile"

@dataclass
class BackgroundImage:
    path: str
    size_mode: BackgroundImageSizeMode = BackgroundImageSizeMode.COVER

    _skia_image: Optional[skia.Image] = field(default=None, repr=False, init=False)

    def get_skia_image(self) -> Optional[skia.Image]:
        if self._skia_image is None:
            try:
                self._skia_image = skia.Image.open(self.path)
            except Exception:
                raise ValueError(f"Could not load background image from: {self.path}")
        return self._skia_image

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
