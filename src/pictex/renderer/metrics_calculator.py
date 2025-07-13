from .structs import RenderMetrics, Line
from ..models import CropMode, Style
from .font_manager import FontManager
from .utils import decoration_line_to_line_y_offset, create_composite_shadow_filter
from typing import Tuple
import skia

class MetricsCalculator:

    def __init__(self, style: Style, font_manager: FontManager) -> None:
        self._style: Style = style
        self._font_manager: FontManager = font_manager

    def calculate(self, lines: list[Line], crop_mode: CropMode) -> RenderMetrics:
        """
        Calculates all necessary geometric properties for rendering.
        This is the core layout engine.
        """
        text_bounds, decorations_bounds = self._build_text_and_decorations_bounds(lines)
        if self._style.outline_stroke:
            text_bounds.outset(self._style.outline_stroke.width / 2, self._style.outline_stroke.width / 2)

        top_pad, right_pad, bottom_pad, left_pad = self._style.padding
        background_bounds = skia.Rect.MakeLTRB(
            text_bounds.left() - left_pad,
            text_bounds.top() - top_pad,
            text_bounds.right() + right_pad,
            text_bounds.bottom() + bottom_pad
        )
        background_bounds.join(decorations_bounds)
        
        canvas_bounds = skia.Rect(background_bounds.left(), background_bounds.top(), background_bounds.right(), background_bounds.bottom())
        canvas_bounds.join(text_bounds) # it only makes sense if padding is negative
        self._apply_shadows_to_canvas_bounds(canvas_bounds, text_bounds, background_bounds, crop_mode)
        draw_origin = (-canvas_bounds.left(), -canvas_bounds.top())

        return RenderMetrics(
            bounds=canvas_bounds,
            background_rect=background_bounds,
            text_rect=text_bounds,
            draw_origin=draw_origin
        )
    
    def _build_text_and_decorations_bounds(self, lines: list[Line]) -> Tuple[skia.Rect, skia.Rect]:
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
                line_y_offset = decoration_line_to_line_y_offset(deco.line, font_metrics)
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

        return (text_bounds, decorations_bounds)

    def _apply_shadows_to_canvas_bounds(
            self,
            canvas_bounds: skia.Rect,
            text_bounds: skia.Rect,
            background_bounds: skia.Rect,
            crop_mode: CropMode
        ) -> None:
        
        if crop_mode == CropMode.CONTENT_BOX:
            return
        
        shadow_filter = create_composite_shadow_filter(self._style.shadows)
        if shadow_filter:
            shadowed_text_bounds = shadow_filter.computeFastBounds(text_bounds)
            canvas_bounds.join(shadowed_text_bounds)

        box_shadow_filter = create_composite_shadow_filter(self._style.box_shadows)
        if box_shadow_filter:
            shadowed_bg_bounds = box_shadow_filter.computeFastBounds(background_bounds)
            canvas_bounds.join(shadowed_bg_bounds)
