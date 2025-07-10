import skia
import os
import struct
from typing import List
from ..models import Style, FontStyle
from .. import logger

class FontManager:
    def __init__(self, style: Style):
        self._style = style
        self._primary_font = self._create_font(self._style.font.family)
        self._fallback_font_typefaces = self._prepare_fallbacks()

    def get_primary_font(self) -> skia.Font:
        return self._primary_font

    def get_fallback_font_typefaces(self) -> List[skia.Typeface]:
        return self._fallback_font_typefaces
    
    def _create_font(self, font_path_or_name) -> skia.Font:
        typeface = self._create_font_typeface(font_path_or_name)
        font = skia.Font(typeface, self._style.font.size)
        font.setSubpixel(True)
        return font

    def _create_font_typeface(self, font_path_or_name: str) -> skia.Typeface:
        if not os.path.exists(font_path_or_name):
            return self._create_system_font_typeface(font_path_or_name)
        
        typeface = skia.Typeface.MakeFromFile(font_path_or_name)
        if not typeface:
            raise ValueError(
                f"Failed to load font from '{font_path_or_name}'. "
                "The file might be corrupted or in an unsupported format."
            )
        
        if typeface.getVariationDesignParameters():
            return self._apply_variations_to_variable_font(typeface)
        
        return typeface
    
    def _create_system_font_typeface(self, font_family: str) -> skia.Font:
        font_style = skia.FontStyle(
            weight=self._style.font.weight,
            width=skia.FontStyle.kNormal_Width,
            slant=self._style.font.style.to_skia_slant()
        )
        typeface = skia.Typeface(font_family, font_style)
        actual_font_family = typeface.getFamilyName()
        if actual_font_family.lower() != font_family.lower():
            logger.warning(
                f"Font '{font_family}' not found in the system. "
                f"Pictex is falling back to '{actual_font_family}'"
            )
        return typeface
    
    def _apply_variations_to_variable_font(self, typeface: skia.Typeface) -> skia.Typeface:
        variations = {
            'wght': float(self._style.font.weight),
            'ital': 1.0 if self._style.font.style == FontStyle.ITALIC else 0.0,
            'slnt': -12.0 if self._style.font.style == FontStyle.OBLIQUE else 0.0,
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
        return typeface.makeClone(font_args)

    def _prepare_fallbacks(self) -> List[skia.Font]:
        user_fallbacks = [self._create_font_typeface(fb) for fb in self._style.font_fallbacks]
        emoji_fallbacks = [
            skia.Typeface("Segoe UI Emoji"),
            skia.Typeface("Apple Color Emoji"),
            skia.Typeface("Noto Color Emoji"),
        ]
        return user_fallbacks + emoji_fallbacks
