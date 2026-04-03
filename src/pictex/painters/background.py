import skia
from .painter import Painter
from ..utils import create_composite_shadow_filter
from ..models import Style, BackgroundImageSizeMode, BorderStyle

class BackgroundPainter(Painter):

    def __init__(self, style: Style, box_bounds: skia.Rect, is_svg: bool):
        super().__init__(style)
        self._box_bounds = box_bounds
        self._is_svg = is_svg

    def paint(self, canvas: skia.Canvas) -> None:
        border_rrect = self._build_rounded_box_rect()
        bg_rrect = self._build_background_rrect()
        self._paint_box_shadows(canvas, border_rrect)
        self._paint_background_color(canvas, bg_rrect)
        self._paint_background_image(canvas, bg_rrect)

    def _build_rounded_box_rect(self) -> skia.RRect:
        box_radius = self._style.border_radius.get()
        if not box_radius:
            return skia.RRect.MakeRect(self._box_bounds)

        return box_radius.apply_corner_radius(self._box_bounds)

    def _build_background_rrect(self) -> skia.RRect:
        """Build the RRect used for painting background colour and image.

        When *both* a **solid** border and a border_radius are present, the
        background rect is inset by ``border.width / 2``, that is, to the
        **centre line** of the border stroke.

        Rationale
        ---------
        Skia's ``drawRRect`` with ``AntiAlias=True`` produces semi-transparent
        AA pixels that extend slightly beyond the shape boundary.  When the
        background fills the full border box, those AA pixels land outside the
        border's outer edge and appear as a colour fringe.

        By inset-ing the background to the centre of the border stroke:

        * The background's outer AA pixels land within the *inner half* of the
          stroke, where the border paint is fully opaque and covers them
          completely, so no fringe is visible.
        * The background never reaches the *outer half* of the stroke, so no
          background pixels can bleed past the border's outer edge.
        * The transition (background → border) stays visually smooth because
          the border naturally absorbs the background's AA edge.

        For dashed or dotted borders the background must fill the full border
        box so that the gaps in the stroke reveal the background colour (CSS
        ``background-clip: border-box`` default behaviour).

        Without a border, or without a border_radius, the border box shape is
        used unchanged (same as :meth:`_build_rounded_box_rect`).
        """
        border = self._style.border.get()
        box_radius = self._style.border_radius.get()
        if not border or border.width <= 0 or not box_radius or border.style != BorderStyle.SOLID:
            return self._build_rounded_box_rect()

        offset = border.width / 2
        inner_rect = self._box_bounds.makeInset(offset, offset)
        return box_radius.apply_corner_radius(inner_rect, offset)

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
        # Gradient shaders are resolved against the full border-box bounds so
        # that gradient colours span the visible element - even when box_rect
        # is the smaller padding-box RRect used to prevent corner bleeding.
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
