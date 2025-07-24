from .alignment import get_line_x_position
from .shadow import create_composite_shadow_filter

import skia

def clone_skia_rect(rect: skia.Rect) -> skia.Rect:
    return skia.Rect.MakeLTRB(rect.left(), rect.top(), rect.right(), rect.bottom())
