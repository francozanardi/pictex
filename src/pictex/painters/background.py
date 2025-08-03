import skia
from .painter import Painter
from ..utils import create_composite_shadow_filter
from ..models import Style, BackgroundImageSizeMode

class BackgroundPainter(Painter):

    def __init__(self, style: Style, box_bounds: skia.Rect, is_svg: bool):
        super().__init__(style)
        self._box_bounds = box_bounds
        self._is_svg = is_svg

    def paint(self, canvas: skia.Canvas) -> None:
        rounded_box_rect = self._build_rounded_box_rect()
        self._paint_box_shadows(canvas, rounded_box_rect)
        self._paint_background_color(canvas, rounded_box_rect)
        self._paint_background_image(canvas, rounded_box_rect)

    def _build_rounded_box_rect(self) -> skia.RRect:
        box_radius = self._style.border_radius.get()
        if not box_radius:
            return skia.RRect.MakeRect(self._box_bounds)

        return box_radius.apply_corner_radius(self._box_bounds)

    def _paint_box_shadows(self, canvas: skia.Canvas, box_rect: skia.RRect):
        if self._is_svg:
            return

        paint = skia.Paint(AntiAlias=True)
        shadow_filter = create_composite_shadow_filter(self._style.box_shadows.get(), should_remove_content=True)
        if shadow_filter:
            paint.setImageFilter(shadow_filter)
            canvas.drawRRect(box_rect, paint)

    def _paint_background_color(self, canvas: skia.Canvas, box_rect: skia.RRect) -> None:
        background_color = self._style.background_color.get()
        if not background_color:
            return

        paint = skia.Paint(AntiAlias=True)
        background_color.apply_to_paint(paint, self._box_bounds)
        canvas.drawRRect(box_rect, paint)

    def _paint_background_image(self, canvas: skia.Canvas, box_rect: skia.RRect):
        background_image_info = self._style.background_image.get()
        if not background_image_info:
            return

        original_image = background_image_info.get_skia_image()
        if not original_image:
            return

        sampling_options = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
        canvas.save()
        canvas.clipRRect(box_rect, doAntiAlias=True)

        paint = skia.Paint(AntiAlias=True)
        if background_image_info.size_mode == BackgroundImageSizeMode.TILE:
            shader = original_image.makeShader(
                skia.TileMode.kRepeat,
                skia.TileMode.kRepeat,
                sampling_options
            )
            paint.setShader(shader)
            canvas.drawRect(self._box_bounds, paint)
            canvas.restore()
            return

        src_rect, dst_rect = self._calculate_cover_contain_rects(
            image_width=original_image.width(),
            image_height=original_image.height(),
            box_rect=self._box_bounds,
            mode=background_image_info.size_mode
        )

        image_to_resize = original_image.makeSubset(src_rect.roundOut())
        resized_image = image_to_resize.resize(
            width=int(dst_rect.width()),
            height=int(dst_rect.height()),
            options=sampling_options
        )

        if not resized_image:
            return

        canvas.drawImage(
            resized_image,
            dst_rect.left(),
            dst_rect.top(),
            sampling_options,
            paint
        )

        canvas.restore()

    def _calculate_cover_contain_rects(
            self, image_width: float, image_height: float, box_rect: skia.Rect, mode: BackgroundImageSizeMode):

        box_width = box_rect.width()
        box_height = box_rect.height()
        img_aspect = image_width / image_height
        box_aspect = box_width / box_height

        if mode == BackgroundImageSizeMode.COVER:
            if img_aspect > box_aspect:
                new_src_width = image_height * box_aspect
                src_x_offset = (image_width - new_src_width) / 2
                src_rect = skia.Rect.MakeXYWH(src_x_offset, 0, new_src_width, image_height)
                return src_rect, box_rect

            new_src_height = image_width / box_aspect
            src_y_offset = (image_height - new_src_height) / 2
            src_rect = skia.Rect.MakeXYWH(0, src_y_offset, image_width, new_src_height)
            return src_rect, box_rect

        elif mode == BackgroundImageSizeMode.CONTAIN:
            src_rect = skia.Rect.MakeWH(image_width, image_height)
            if img_aspect > box_aspect:
                new_dst_height = box_width / img_aspect
                dst_y_offset = (box_height - new_dst_height) / 2
                dst_rect = skia.Rect.MakeXYWH(box_rect.left(), box_rect.top() + dst_y_offset, box_width, new_dst_height)
                return src_rect, dst_rect

            new_dst_width = box_height * img_aspect
            dst_x_offset = (box_width - new_dst_width) / 2
            dst_rect = skia.Rect.MakeXYWH(box_rect.left() + dst_x_offset, box_rect.top(), new_dst_width, box_height)
            return src_rect, dst_rect

        raise ValueError(f"Unknown mode: {mode}")
