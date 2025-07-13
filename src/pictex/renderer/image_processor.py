import skia
from ..models import CropMode, Box
from typing import Tuple, Optional
from .structs import RenderMetrics
import numpy as np
from ..image import Image

class ImageProcessor:

    def process(self, image: skia.Image, metrics: RenderMetrics, crop_mode: CropMode) -> Image:
        bg_rect = metrics.background_rect
        content_rect = skia.Rect.MakeLTRB(bg_rect.left(), bg_rect.top(), bg_rect.right(), bg_rect.bottom())
        content_rect.offset(metrics.draw_origin)
        if crop_mode == CropMode.SMART:
            crop_rect = self._get_trim_rect(image)
            if crop_rect:
                image = image.makeSubset(crop_rect)
                content_rect.offset(-crop_rect.left(), -crop_rect.top())
        
        content_box = Box(
            x=int(content_rect.left()),
            y=int(content_rect.top()),
            width=int(content_rect.width()),
            height=int(content_rect.height())
        )

        return Image(skia_image=image, content_box=content_box)

    def _get_trim_rect(self, image: skia.Image) -> Optional[skia.Rect]:
        """
        Crops the image by removing transparent borders.
        """
        width, height = image.width(), image.height()
        if width == 0 or height == 0:
            return None
        
        pixels = np.frombuffer(image.tobytes(), dtype=np.uint8).reshape((height, width, 4))
        alpha_channel = pixels[:, :, 3]
        coords = np.argwhere(alpha_channel > 0)
        if coords.size == 0:
            # Image is fully transparent
            return None

        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        return skia.IRect.MakeLTRB(x_min, y_min, x_max + 1, y_max + 1)
