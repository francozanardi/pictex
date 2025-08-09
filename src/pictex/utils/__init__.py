from .alignment import get_line_x_position
from .shadow import create_composite_shadow_filter
from .cache import cached_method, cached_property, Cacheable
from math import ceil, floor
import skia

def clone_skia_rect(rect: skia.Rect) -> skia.Rect:
    return skia.Rect.MakeLTRB(rect.left(), rect.top(), rect.right(), rect.bottom())

def to_int_skia_rect(rect: skia.Rect) -> skia.Rect:
    return skia.Rect.MakeLTRB(
        floor(rect.left()),
        floor(rect.top()),
        ceil(rect.right()),
        ceil(rect.bottom()),
    )
