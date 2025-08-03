from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
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

    def __deepcopy__(self, memo):
        return BackgroundImage(
            path=deepcopy(self.path, memo),
            size_mode=deepcopy(self.size_mode, memo)
        )
