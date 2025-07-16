from ...models import Shadow
import skia
from typing import Optional

def create_composite_shadow_filter(shadows: list[Shadow]) -> Optional[skia.ImageFilter]:
    if len(shadows) == 0:
        return None

    skia_shadow_filters = []
    for shadow in shadows:
        skia_shadow_filters.append(skia.ImageFilters.DropShadow(
            dx=shadow.offset[0], dy=shadow.offset[1],
            sigmaX=shadow.blur_radius, sigmaY=shadow.blur_radius,
            color=skia.Color(
                shadow.color.r, shadow.color.g,
                shadow.color.b, shadow.color.a
            )
        ))

    if len(skia_shadow_filters) == 1:
        return skia_shadow_filters[0]

    composite_filter = skia_shadow_filters[0]
    for i in range(1, len(skia_shadow_filters)):
        composite_filter = skia.ImageFilters.Compose(skia_shadow_filters[i], composite_filter)

    return composite_filter