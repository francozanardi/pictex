import skia
from typing import Optional, Tuple
import numpy as np

from ..models import Style, Alignment, DecorationLine, Shadow, CropMode, Box
from .structs import Line, RenderMetrics
from .shaper import TextShaper
from .font_manager import FontManager

class SkiaRenderer:
    """Handles the drawing logic using Skia."""

    def __init__(self, style: Style):
        self._style = style
        self._font_manager = FontManager(style)
        self._shaper = TextShaper(style, self._font_manager)

    def render(self, text: str, crop_mode: CropMode) -> Tuple[skia.Image, Box]:
        """Renders the text with the given style onto a perfectly sized Skia surface."""

        lines = self._shaper.shape(text)

        metrics = self._calculate_metrics(lines, crop_mode)
        canvas_width = int(metrics.bounds.width())
        canvas_height = int(metrics.bounds.height())
        if canvas_width <= 0 or canvas_height <= 0:
            return skia.Image.MakeRasterN32Premul(1, 1)

        image_info = skia.ImageInfo.MakeN32Premul(canvas_width, canvas_height)
        surface = skia.Surface(image_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(metrics.draw_origin[0], metrics.draw_origin[1])

        self._draw_background(canvas, metrics)
        
        text_paint = skia.Paint(AntiAlias=True)
        self._style.color.apply_to_paint(text_paint, metrics.text_rect)

        self._draw_shadow(text_paint)
        outline_stroke_paint = self._draw_outline_stroke(metrics)
        self._draw_text(lines, canvas, text_paint, outline_stroke_paint, metrics)
        self._draw_decorations(lines, canvas, metrics)
        
        final_image = surface.makeImageSnapshot()
        return self._post_process_image(final_image, metrics, crop_mode)

    def _calculate_metrics(self, lines: list[Line], crop_mode: CropMode) -> RenderMetrics:
        """
        Calculates all necessary geometric properties for rendering.
        This is the core layout engine.
        """
        line_gap = self._style.font.line_height * self._style.font.size if lines else 0

        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()
        decorations_bounds = skia.Rect.MakeEmpty()

        for line in lines:
            line_bounds = skia.Rect.MakeLTRB(line.bounds.left(), line.bounds.top(), line.bounds.right(), line.bounds.bottom())
            line_bounds.offset(0, current_y)
            text_bounds.join(line_bounds)

            for deco in self._style.decorations:
                primary_font = self._font_manager.get_primary_font()
                font_metrics = primary_font.getMetrics()
                line_y_offset = self._decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                half_thickness = deco.thickness / 2
                deco_rect = skia.Rect.MakeLTRB(
                    line_bounds.left(), 
                    line_y - half_thickness, 
                    line_bounds.right(), 
                    line_y + half_thickness
                )
                decorations_bounds.join(deco_rect)
            
            current_y += line_gap

        if self._style.outline_stroke:
            text_bounds.outset(self._style.outline_stroke.width / 2, self._style.outline_stroke.width / 2)

        top_pad, right_pad, bottom_pad, left_pad = self._style.padding
        background_rect = skia.Rect.MakeLTRB(
            text_bounds.left() - left_pad,
            text_bounds.top() - top_pad,
            text_bounds.right() + right_pad,
            text_bounds.bottom() + bottom_pad
        )
        background_rect.join(decorations_bounds)

        full_bounds = skia.Rect(background_rect.left(), background_rect.top(), background_rect.right(), background_rect.bottom())
        full_bounds.join(text_bounds) # it only makes sense if padding is negative
        
        if crop_mode != CropMode.CONTENT_BOX:
            shadow_filter = self._create_composite_shadow_filter(self._style.shadows)
            if shadow_filter:
                shadowed_text_bounds = shadow_filter.computeFastBounds(text_bounds)
                full_bounds.join(shadowed_text_bounds)

            box_shadow_filter = self._create_composite_shadow_filter(self._style.box_shadows)
            if box_shadow_filter:
                shadowed_bg_bounds = box_shadow_filter.computeFastBounds(background_rect)
                full_bounds.join(shadowed_bg_bounds)

        draw_origin = (-full_bounds.left(), -full_bounds.top())

        return RenderMetrics(
            bounds=full_bounds,
            background_rect=background_rect,
            text_rect=text_bounds,
            draw_origin=draw_origin
        )
    
    def _draw_background(self, canvas: skia.Canvas, metrics: RenderMetrics) -> None:
        bg_paint = skia.Paint(AntiAlias=True)
        self._style.background.color.apply_to_paint(bg_paint, metrics.background_rect)

        shadow_filter = self._create_composite_shadow_filter(self._style.box_shadows)
        if shadow_filter:
            bg_paint.setImageFilter(shadow_filter)

        radius = self._style.background.corner_radius
        if radius > 0:
            canvas.drawRoundRect(metrics.background_rect, radius, radius, bg_paint)
        else:
            canvas.drawRect(metrics.background_rect, bg_paint)

    def _create_composite_shadow_filter(self, shadows: list[Shadow]) -> Optional[skia.ImageFilter]:
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

    def _draw_shadow(self, text_paint: skia.Paint) -> None:
        filter = self._create_composite_shadow_filter(self._style.shadows)
        if not filter:
            return
        text_paint.setImageFilter(filter)

    def _draw_outline_stroke(self, metrics: RenderMetrics) -> Optional[skia.Paint]:
        if not self._style.outline_stroke:
            return None
        
        paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=self._style.outline_stroke.width
        )
        self._style.outline_stroke.color.apply_to_paint(paint, metrics.text_rect)
        return paint

    def _draw_text(
            self,
            lines: list[Line],
            canvas: skia.Canvas,
            text_paint: skia.Paint,
            outline_paint: Optional[skia.Paint],
            metrics: RenderMetrics
        ) -> None:
        line_gap = self._style.font.line_height * self._style.font.size
        current_y = 0
        block_width = metrics.text_rect.width()
        
        for line in lines:
            draw_x_start = self._get_line_x(self._style.alignment, block_width, line.width)
            current_x = draw_x_start
            
            for run in line.runs:
                if outline_paint:
                    canvas.drawString(run.text, current_x, current_y, run.font, outline_paint)
                canvas.drawString(run.text, current_x, current_y, run.font, text_paint)
                current_x += run.width
            
            current_y += line_gap

    def _draw_decorations(
            self,
            lines: list[Line],
            canvas: skia.Canvas,
            metrics: RenderMetrics
        ) -> None:

        if not self._style.decorations:
            return
        
        primary_font = self._font_manager.get_primary_font()
        font_metrics = primary_font.getMetrics()
        line_gap = self._style.font.line_height * self._style.font.size
        current_y = 0
        block_width = metrics.text_rect.width()
        
        for line in lines:
            if not line.runs:
                current_y += line_gap
                continue

            line_x_start = self._get_line_x(self._style.alignment, block_width, line.width)
            
            for deco in self._style.decorations:                
                line_y_offset = self._decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                
                paint = skia.Paint(AntiAlias=True, StrokeWidth=deco.thickness)
                half_thickness = deco.thickness / 2
                if deco.color:
                    color = deco.color
                    bounds = skia.Rect.MakeLTRB(line_x_start, line_y - half_thickness, line_x_start + line.width, line_y + half_thickness)
                    color.apply_to_paint(paint, bounds)
                else:
                    color = self._style.color
                    color.apply_to_paint(paint, metrics.text_rect)

                canvas.drawLine(line_x_start, line_y, line_x_start + line.width, line_y, paint)

            current_y += line_gap

    def _decoration_line_to_line_y_offset(self, decoration_line: DecorationLine, font_metrics) -> float:
        if decoration_line == DecorationLine.UNDERLINE:
            return font_metrics.fUnderlinePosition
        
        return font_metrics.fStrikeoutPosition

    def _get_line_x(self, align: Alignment, block_width: float, line_width: float) -> float:
        if align == Alignment.RIGHT:
            return block_width - line_width
        if align == Alignment.CENTER:
            return (block_width - line_width) / 2
        
        return 0 # Alignment.LEFT
    
    def _post_process_image(self, image: skia.Image, metrics: RenderMetrics, crop_mode: CropMode) -> Tuple[skia.Image, Box]:
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

        return (image, content_box)

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
