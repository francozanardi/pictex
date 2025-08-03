from __future__ import annotations
from typing import Callable, TYPE_CHECKING
import skia

if TYPE_CHECKING:
    from ..nodes import Node
    from ..models import SizeValue

class SizeResolver:

    def __init__(self, node: Node):
        self._node = node
        self._intrinsic_bounds: skia.Rect | None = None

    def resolve(self) -> skia.Rect:
        size = self._node.computed_styles.size.get()
        if not size:
            return self._get_intrinsic_bounds()

        padding = self._node.computed_styles.padding.get()
        border = self._node.computed_styles.border.get()
        border_width = border.width if border else 0

        horizontal_spacing = padding.left + padding.right + (border_width * 2)
        vertical_spacing = padding.top + padding.bottom + (border_width * 2)

        box_width = self._get_axis_size(
            size.width,
            lambda: self._get_intrinsic_bounds().width() + horizontal_spacing,
            lambda: self._get_background_value("width"),
            lambda: self._get_container_value("width")
        )
        box_height = self._get_axis_size(
            size.height,
            lambda: self._get_intrinsic_bounds().height() + vertical_spacing,
            lambda: self._get_background_value("height"),
            lambda: self._get_container_value("height")
        )

        content_width = max(0, box_width - horizontal_spacing)
        content_height = max(0, box_height - vertical_spacing)

        return skia.Rect.MakeWH(content_width, content_height)

    def _get_intrinsic_bounds(self) -> skia.Rect:
        if self._intrinsic_bounds is None:
            self._intrinsic_bounds = self._node._compute_intrinsic_content_bounds()
        return self._intrinsic_bounds

    def _get_background_value(self, axis: str) -> float:
        background_image = self._node.computed_styles.background_image.get()
        if not background_image:
            raise ValueError("Cannot use 'fit-background-image' on an element without a background image.")

        image = background_image.get_skia_image()
        if not image:
            raise ValueError(f"Background image for node could not be loaded: {background_image.path}")

        return getattr(image, axis)()

    def _get_container_value(self, axis: str) -> float:
        parent = self._node.parent
        if not parent:
            raise ValueError("Cannot use 'percent' size on a root element without a parent.")

        parent_size = parent.computed_styles.size.get()
        if not parent_size or parent_size.width.mode == 'fit-content' or parent_size.height.mode == 'fit-content':
            raise ValueError("Cannot use 'percent' size if parent element has 'fit-content' size.")

        return getattr(parent.content_bounds, axis)()

    def _get_axis_size(
            self,
            value: 'SizeValue',
            get_content_value: Callable[[], float],
            get_background_value: Callable[[], float],
            get_container_value: Callable[[], float]
    ) -> float:
        if value.mode == 'absolute':
            return value.value
        if value.mode == 'percent':
            return get_container_value() * (value.value / 100.0)
        if value.mode == 'fit-content':
            return get_content_value()
        if value.mode == 'fit-background-image':
            return get_background_value()
        raise ValueError(f"Unsupported size mode: {value.mode}")
