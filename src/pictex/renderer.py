import skia
import os
import struct
from dataclasses import dataclass
from typing import Optional

from .models import Style, Alignment, FontStyle, DecorationLine, Shadow
from . import logger

@dataclass
class RenderMetrics:
    """A helper class to store all calculated dimensions for rendering."""
    bounds: skia.Rect
    background_rect: skia.Rect
    text_rect: skia.Rect
    draw_origin: tuple[float, float]

class SkiaRenderer:
    """Handles the actual drawing logic using Skia."""

    def render(self, text: str, style: Style) -> skia.Image:
        """Renders the text with the given style onto a perfectly sized Skia surface."""
        font = self._create_font(style)
        font.setSubpixel(True)

        metrics = self._calculate_metrics(text, font, style)
        canvas_width = int(metrics.bounds.width())
        canvas_height = int(metrics.bounds.height())
        if canvas_width <= 0 or canvas_height <= 0:
            return skia.Image.MakeRasterN32Premul(1, 1)

        image_info = skia.ImageInfo.MakeN32Premul(canvas_width, canvas_height)
        surface = skia.Surface(image_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(metrics.draw_origin[0], metrics.draw_origin[1])

        self._draw_background(canvas, style, metrics)
        
        text_paint = skia.Paint(AntiAlias=True)
        style.color.apply_to_paint(text_paint, metrics.text_rect)

        self._draw_shadow(text_paint, style)
        outline_stroke_paint = self._draw_outline_stroke(style, metrics)
        self._draw_text(text, canvas, text_paint, outline_stroke_paint, font, style, metrics)
        self._draw_decorations(text, canvas, font, style, metrics)
        
        return surface.makeImageSnapshot()
    
    def _create_font(self, style: Style) -> skia.Font:
        font_path_or_name = style.font.family

        if not os.path.exists(font_path_or_name):
            font_style = skia.FontStyle(
                weight=style.font.weight,
                width=skia.FontStyle.kNormal_Width,
                slant=style.font.style.to_skia_slant()
            )
            typeface = skia.Typeface(font_path_or_name, font_style)
            actual_font_family = typeface.getFamilyName()
            if actual_font_family.lower() != font_path_or_name.lower():
                logger.warning(
                    f"Font '{font_path_or_name}' not found in the system. "
                    f"Pictex is falling back to '{actual_font_family}'"
                )
            return skia.Font(typeface, style.font.size)
        
        typeface = skia.Typeface.MakeFromFile(font_path_or_name)
        if not typeface:
            raise ValueError(
                f"Failed to load font from '{font_path_or_name}'. "
                "The file might be corrupted or in an unsupported format."
            )
        
        if typeface.getVariationDesignParameters():
            # It's a variable font
            variations = {
                'wght': float(style.font.weight),
                'ital': 1.0 if style.font.style == FontStyle.ITALIC else 0.0,
                'slnt': -12.0 if style.font.style == FontStyle.OBLIQUE else 0.0,
            }
            to_four_char_code = lambda tag: struct.unpack('!I', tag.encode('utf-8'))[0]
            available_axes_tags = { axis.tag for axis in typeface.getVariationDesignParameters() }
            coordinates_list = [
                skia.FontArguments.VariationPosition.Coordinate(axis=to_four_char_code(tag), value=value)
                for tag, value in variations.items()
                if to_four_char_code(tag) in available_axes_tags
            ]

            if coordinates_list:
                coordinates = skia.FontArguments.VariationPosition.Coordinates(coordinates_list)
                variation_position = skia.FontArguments.VariationPosition(coordinates)
                font_args = skia.FontArguments()
                font_args.setVariationDesignPosition(variation_position)
                typeface = typeface.makeClone(font_args)
        
        return skia.Font(typeface, style.font.size)

    def _calculate_metrics(self, text: str, font: skia.Font, style: Style) -> RenderMetrics:
        """
        Calculates all necessary geometric properties for rendering.
        This is the core layout engine.
        """
        lines = text.split('\n')
        font_metrics = font.getMetrics()
        line_gap = style.font.line_height * style.font.size

        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()
        decorations_bounds = skia.Rect.MakeEmpty()

        for line in lines:
            line_bounds = skia.Rect()
            line_width = font.measureText(line, bounds=line_bounds)
            
            line_bounds.offset(0, current_y)
            text_bounds.join(line_bounds)

            for deco in style.decorations:
                line_y_offset = self._decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                half_thickness = deco.thickness / 2
                deco_rect = skia.Rect.MakeLTRB(
                    0, 
                    line_y - half_thickness, 
                    line_width, 
                    line_y + half_thickness
                )
                decorations_bounds.join(deco_rect)
            
            current_y += line_gap

        if style.outline_stroke:
            text_bounds.outset(style.outline_stroke.width / 2, style.outline_stroke.width / 2)

        top_pad, right_pad, bottom_pad, left_pad = style.padding
        background_rect = skia.Rect.MakeLTRB(
            text_bounds.left() - left_pad,
            text_bounds.top() - top_pad,
            text_bounds.right() + right_pad,
            text_bounds.bottom() + bottom_pad
        )
        background_rect.join(decorations_bounds)

        full_bounds = skia.Rect(background_rect.left(), background_rect.top(), background_rect.right(), background_rect.bottom())
        full_bounds.join(text_bounds) # it only makes sense if padding is negative
        
        shadow_filter = self._create_composite_shadow_filter(style.shadows)
        if shadow_filter:
            shadowed_text_bounds = shadow_filter.computeFastBounds(text_bounds)
            full_bounds.join(shadowed_text_bounds)

        box_shadow_filter = self._create_composite_shadow_filter(style.box_shadows)
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
    
    def _draw_background(self, canvas: skia.Canvas, style: Style, metrics: RenderMetrics) -> None:
        bg_paint = skia.Paint(AntiAlias=True)
        style.background.color.apply_to_paint(bg_paint, metrics.background_rect)

        shadow_filter = self._create_composite_shadow_filter(style.box_shadows)
        if shadow_filter:
            bg_paint.setImageFilter(shadow_filter)

        radius = style.background.corner_radius
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

        return skia.ImageFilters.Merge(skia_shadow_filters)

    def _draw_shadow(self, text_paint: skia.Paint, style: Style) -> None:
        filter = self._create_composite_shadow_filter(style.shadows)
        if not filter:
            return
        text_paint.setImageFilter(filter)

    def _draw_outline_stroke(self, style: Style, metrics: RenderMetrics) -> Optional[skia.Paint]:
        if not style.outline_stroke:
            return None
        
        paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=style.outline_stroke.width
        )
        style.outline_stroke.color.apply_to_paint(paint, metrics.text_rect)
        return paint

    def _draw_text(
            self,
            text: str,
            canvas: skia.Canvas,
            text_paint: skia.Paint,
            outline_paint: Optional[skia.Paint],
            font: skia.Font,
            style: Style,
            metrics: RenderMetrics
        ) -> None:
        lines = text.split('\n')
        line_gap = style.font.line_height * style.font.size
        current_y = 0
        
        for line in lines:
            line_width = font.measureText(line)
            draw_x = self._get_line_x(style.alignment, metrics.text_rect.width(), line_width)

            if outline_paint:
                canvas.drawString(line, draw_x, current_y, font, outline_paint)

            canvas.drawString(line, draw_x, current_y, font, text_paint)
            current_y += line_gap

    def _draw_decorations(
            self,
            text: str,
            canvas: skia.Canvas,
            font: skia.Font,
            style: Style,
            metrics: RenderMetrics
        ) -> None:

        if len(style.decorations) == 0:
            return
        
        lines = text.split('\n')
        line_gap = style.font.line_height * style.font.size
        font_metrics = font.getMetrics()
        
        current_y = 0
        for line in lines:
            line_width = font.measureText(line)
            
            for deco in style.decorations:                
                line_y_offset = self._decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                line_x = self._get_line_x(style.alignment, metrics.text_rect.width(), line_width)

                paint = skia.Paint(AntiAlias=True, StrokeWidth=deco.thickness)
                half_thickness = deco.thickness / 2
                if deco.color:
                    color = deco.color
                    bounds = skia.Rect.MakeLTRB(line_x, line_y - half_thickness, line_x + line_width, line_y + half_thickness)
                    color.apply_to_paint(paint, bounds)
                else:
                    color = style.color
                    color.apply_to_paint(paint, metrics.text_rect)

                canvas.drawLine(line_x, line_y, line_x + line_width, line_y, paint)

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