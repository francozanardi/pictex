import skia
import os
import struct
from typing import List, Optional
import warnings
from ..models import Style, FontStyle, FontSmoothing, FontMetrics
from ..exceptions import FontNotFoundWarning
from .typeface_loader import TypefaceLoader
from .. import utils

class FontManager:

    def __init__(self, style: Style, font_smoothing: FontSmoothing):
        self._style = style
        self._font_smoothing = font_smoothing
        self._font_metrics: dict[str, FontMetrics] = {}
        self._fallback_font_typefaces = self._prepare_fallbacks()
        self._primary_font = self._create_primary_font()

    def get_primary_font(self) -> skia.Font:
        return self._primary_font

    def get_fallback_font_typefaces(self) -> List[skia.Typeface]:
        return self._fallback_font_typefaces
    
    def get_font_metrics(self, font: skia.Font) -> FontMetrics:
        # NOTE: keep in mind we're ignoring the font style in the cache key,
        # It could be an issue when we're using a variable typeface (like weight or slant variations) since the metrics could change.
        # I'm not sure if `font.getSize()` is considering the variations, or it's just returning the received font size.

        # We're going to disable this cache for now, since it could cause these issues, and probably 'getMetrics()' is not an expensive call.
        # key: str = font.getTypeface().getFamilyName() + "_" + str(font.getSize())
        # if key in self._font_metrics:
        #     return self._font_metrics[key]
        
        font_metrics = font.getMetrics()
        metrics = FontMetrics(
            ascent=abs(font_metrics.fAscent),
            descent=font_metrics.fDescent,
            leading=font_metrics.fLeading,
            underline_position=font_metrics.fUnderlinePosition,
            strikethrough_position=font_metrics.fStrikeoutPosition
        )
        # self._font_metrics[key] = metrics
        return metrics
    
    def _create_primary_font(self) -> skia.Font:
        font_path_or_name = self._style.font_family.get()
        typeface: Optional[skia.Typeface] = None
        if font_path_or_name:
            typeface = self._create_font_typeface(font_path_or_name)
        
        if not typeface and len(self._fallback_font_typefaces) > 0:
            # the first fallback font typeface is promoted to primary font
            typeface = self._fallback_font_typefaces.pop(0)

        if not typeface:
            typeface = TypefaceLoader.load_default()
            if utils.is_variable_font(typeface):
                typeface = self._apply_variations_to_variable_font(typeface)
        
        return self._create_font(typeface)
    
    def _create_font(self, typeface: skia.Typeface) -> skia.Font:
        font = skia.Font(typeface, self._style.font_size.get())
        font.setLinearMetrics(True)
        font.setForceAutoHinting(True)
        font.setHinting(skia.FontHinting.kSlight)
        if self._font_smoothing == FontSmoothing.SUBPIXEL:
            font.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
            font.setSubpixel(True)
        else: # STANDARD
            font.setEdging(skia.Font.Edging.kAntiAlias)
            font.setSubpixel(False)
        return font

    def _create_font_typeface(self, font_path_or_name: str) -> Optional[skia.Typeface]:
        if not os.path.exists(font_path_or_name):
            return self._create_system_font_typeface(font_path_or_name)
        
        typeface = TypefaceLoader.load_from_file(font_path_or_name)
        if not typeface:
            raise ValueError(
                f"Failed to load font from '{font_path_or_name}'. "
                "The file might be corrupted or in an unsupported format."
            )
        
        if utils.is_variable_font(typeface):
            return self._apply_variations_to_variable_font(typeface)
        
        return typeface
    
    def _create_system_font_typeface(self, font_family: str) -> Optional[skia.Typeface]:
        font_style = skia.FontStyle(
            weight=self._style.font_weight.get(),
            width=skia.FontStyle.kNormal_Width,
            slant=self._style.font_style.get().to_skia_slant()
        )
        typeface = TypefaceLoader.load_system_font(font_family, font_style)
        actual_font_family = typeface.getFamilyName() if typeface else ""
        if typeface is None or actual_font_family.lower() != font_family.lower():
            warning_message = f"Font '{font_family}' was not found. It will be ignored."
            warnings.warn(FontNotFoundWarning(warning_message))
            return None
        
        return typeface
    
    def _apply_variations_to_variable_font(self, typeface: skia.Typeface) -> skia.Typeface:
        variations = {
            'wght': float(self._style.font_weight.get()),
            'ital': 1.0 if self._style.font_style.get() == FontStyle.ITALIC else 0.0,
            'slnt': -12.0 if self._style.font_style.get() == FontStyle.OBLIQUE else 0.0,
        }
        to_four_char_code = lambda tag: struct.unpack('!I', tag.encode('utf-8'))[0]
        available_axes_tags = { axis.tag for axis in typeface.getVariationDesignParameters() }
        coordinates_list = [
            skia.FontArguments.VariationPosition.Coordinate(axis=to_four_char_code(tag), value=value)
            for tag, value in variations.items()
            if to_four_char_code(tag) in available_axes_tags
        ]

        if not coordinates_list:
            return typeface
        
        coordinates = skia.FontArguments.VariationPosition.Coordinates(coordinates_list)
        variation_position = skia.FontArguments.VariationPosition(coordinates)
        font_args = skia.FontArguments()
        font_args.setVariationDesignPosition(variation_position)
        return TypefaceLoader.clone_with_arguments(typeface, font_args)

    def _prepare_fallbacks(self) -> List[skia.Font]:
        user_fallbacks = [self._create_font_typeface(fb) for fb in self._style.font_fallbacks.get()]
        return list(filter(lambda e: e, user_fallbacks))
