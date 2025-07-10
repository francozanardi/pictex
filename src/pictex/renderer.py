import skia
import os
import struct
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

from .models import Style, Alignment, FontStyle, DecorationLine, Shadow, CropMode, Box
from . import logger

@dataclass
class RenderMetrics:
    """A helper class to store all calculated dimensions for rendering."""
    bounds: skia.Rect
    background_rect: skia.Rect
    text_rect: skia.Rect
    draw_origin: tuple[float, float]

@dataclass
class TextRun:
    """Represents a segment of text that can be rendered with a single font."""
    text: str
    font: skia.Font
    width: float = 0.0

@dataclass
class Line:
    """Represents a full line composed of multiple TextRuns."""
    runs: list[TextRun]
    width: float
    bounds: skia.Rect

class SkiaRenderer:
    """Handles the drawing logic using Skia."""

    def render(self, text: str, style: Style, crop_mode: CropMode) -> Tuple[skia.Image, Box]:
        """Renders the text with the given style onto a perfectly sized Skia surface."""

        lines = self._shape_text_into_lines(text, style)

        metrics = self._calculate_metrics(lines, style, crop_mode)
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
        self._draw_text(lines, canvas, text_paint, outline_stroke_paint, style, metrics)
        self._draw_decorations(lines, canvas, style, metrics)
        
        final_image = surface.makeImageSnapshot()
        return self._post_process_image(final_image, metrics, crop_mode)
    
    def _create_font(self, style: Style, font_path_or_name: str) -> skia.Font:
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
            font = skia.Font(typeface, style.font.size)
            font.setSubpixel(True)
            return font
        
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
        
        font = skia.Font(typeface, style.font.size)
        font.setSubpixel(True)
        return font

    def _calculate_metrics(self, lines: list[Line], style: Style, crop_mode: CropMode) -> RenderMetrics:
        """
        Calculates all necessary geometric properties for rendering.
        This is the core layout engine.
        """
        line_gap = style.font.line_height * style.font.size if lines else 0

        current_y = 0
        text_bounds = skia.Rect.MakeEmpty()
        decorations_bounds = skia.Rect.MakeEmpty()

        for line in lines:
            line_bounds = skia.Rect.MakeLTRB(line.bounds.left(), line.bounds.top(), line.bounds.right(), line.bounds.bottom())
            line_bounds.offset(0, current_y)
            text_bounds.join(line_bounds)

            for deco in style.decorations:
                primary_font = self._create_font(style, style.font.family)
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
        
        if crop_mode != CropMode.CONTENT_BOX:
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
    
    def _shape_text_into_lines(self, text: str, style: Style) -> list[Line]:
        """
        Breaks a text string into lines and runs, applying font fallbacks.
        This is the core of the text shaping and fallback logic.
        """
        primary_font = self._create_font(style, style.font.family)
        fallback_fonts = [self._create_font(style, fb) for fb in style.font_fallbacks]
        
        emoji_fallbacks = [
            skia.Typeface("Segoe UI Emoji"), # Windows
            skia.Typeface("Apple Color Emoji"), # macOS
            skia.Typeface("Noto Color Emoji"), # Linux
        ]
        fallback_typefaces = [f.getTypeface() for f in fallback_fonts] + [tf for tf in emoji_fallbacks if tf]
        
        shaped_lines: list[Line] = []
        for line_text in text.split('\n'):
            if not line_text:
                # Handle empty lines by creating a placeholder with correct height
                line = Line(runs=[], width=0, bounds=skia.Rect.MakeEmpty())
                font_metrics = primary_font.getMetrics()
                line.bounds = skia.Rect.MakeLTRB(0, font_metrics.fAscent, 0, font_metrics.fDescent)
                shaped_lines.append(line)
                continue

            current_run_text = ""
            current_font = primary_font
            line_runs: list[TextRun] = []

            for char in line_text:
                glyph_id = current_font.unicharToGlyph(ord(char))
                
                if glyph_id != 0:
                    # Character is supported, continue the current run
                    current_run_text += char
                    continue

                # Glyph not found in current font
                if current_run_text:
                    run = TextRun(current_run_text, current_font)
                    line_runs.append(run)
                
                # Find a new font that supports this character
                found_fallback = False
                for typeface in fallback_typefaces:
                    if typeface.unicharToGlyph(ord(char)) != 0:
                        # Found a fallback!
                        current_font = primary_font.makeWithSize(primary_font.getSize())
                        current_font.setTypeface(typeface)
                        found_fallback = True
                        break
                
                if not found_fallback:
                    current_font = primary_font

                # If no fallback supports it, revert to the primary font
                # which will render the '.notdef' (e.g., '□') glyph.
                current_run_text = char
            
            # Add the last run
            if current_run_text:
                run = TextRun(current_run_text, current_font)
                line_runs.append(run)

            # Calculate widths for the completed line
            line_width = 0
            line_bounds = skia.Rect.MakeEmpty()
            for run in line_runs:
                run.width = run.font.measureText(run.text)
                run_bounds = skia.Rect()
                run.font.measureText(run.text, bounds=run_bounds)
                run_bounds.offset(line_width, 0)
                line_bounds.join(run_bounds)
                line_width += run.width

            shaped_lines.append(Line(runs=line_runs, width=line_width, bounds=line_bounds))
            
        return shaped_lines
    
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

        if len(skia_shadow_filters) == 1:
            return skia_shadow_filters[0]

        composite_filter = skia_shadow_filters[0]
        for i in range(1, len(skia_shadow_filters)):
            composite_filter = skia.ImageFilters.Compose(skia_shadow_filters[i], composite_filter)

        return composite_filter

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
            lines: list[Line],
            canvas: skia.Canvas,
            text_paint: skia.Paint,
            outline_paint: Optional[skia.Paint],
            style: Style,
            metrics: RenderMetrics
        ) -> None:
        line_gap = style.font.line_height * style.font.size
        current_y = 0
        block_width = metrics.text_rect.width()
        
        for line in lines:
            draw_x_start = self._get_line_x(style.alignment, block_width, line.width)
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
            style: Style,
            metrics: RenderMetrics
        ) -> None:

        if not style.decorations:
            return
        
        primary_font = self._create_font(style, style.font.family)
        font_metrics = primary_font.getMetrics()
        line_gap = style.font.line_height * style.font.size
        current_y = 0
        block_width = metrics.text_rect.width()
        
        for line in lines:
            if not line.runs:
                current_y += line_gap
                continue

            line_x_start = self._get_line_x(style.alignment, block_width, line.width)
            
            for deco in style.decorations:                
                line_y_offset = self._decoration_line_to_line_y_offset(deco.line, font_metrics)
                line_y = current_y + line_y_offset
                
                paint = skia.Paint(AntiAlias=True, StrokeWidth=deco.thickness)
                half_thickness = deco.thickness / 2
                if deco.color:
                    color = deco.color
                    bounds = skia.Rect.MakeLTRB(line_x_start, line_y - half_thickness, line_x_start + line.width, line_y + half_thickness)
                    color.apply_to_paint(paint, bounds)
                else:
                    color = style.color
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
