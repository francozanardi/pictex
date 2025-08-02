from dataclasses import dataclass
import skia
from ..public import CropMode, FontSmoothing

@dataclass
class RenderMetrics:
    """A helper class to store all calculated dimensions for rendering."""
    bounds: skia.Rect
    background_rect: skia.Rect
    text_rect: skia.Rect
    draw_origin: tuple[float, float]

@dataclass(frozen=True)
class RenderProps:
    is_svg: bool
    crop_mode: CropMode
    font_smoothing: FontSmoothing
