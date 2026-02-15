"""
HarfBuzz text shaping integration for PicTex.

This module provides accurate text shaping using HarfBuzz, which correctly
handles zero-width characters, BiDi control characters, complex scripts,
and emoji composition.
"""
import skia
import uharfbuzz as hb
from typing import NamedTuple
from dataclasses import dataclass

from .skia_table_loader import SkiaTableLoader


@dataclass
class ShapedGlyph:
    """A single shaped glyph with positioning information in points."""
    glyph_id: int
    x_advance: float
    y_advance: float
    x_offset: float
    y_offset: float


class ShapedText(NamedTuple):
    """Result of HarfBuzz text shaping."""
    glyphs: list[ShapedGlyph]
    width: float


class HarfBuzzShaper:
    """
    Shapes text using HarfBuzz for accurate glyph positioning.
    
    Maintains a cache of HarfBuzz fonts to avoid repeatedly loading
    the same font data. For system fonts, keeps table loaders alive
    to prevent garbage collection issues.
    """
    
    def __init__(self):
        self._font_cache: dict[tuple[int, float], tuple[hb.Font, int, object]] = {}
    
    def shape(self, text: str, font: skia.Font) -> ShapedText:
        """
        Shape text using HarfBuzz.
        
        Args:
            text: The text to shape
            font: The Skia font to use for shaping
        
        Returns:
            ShapedText with glyphs and total width
        """
        hb_font, upem = self._get_or_create_hb_font(font)
        font_size = font.getSize()
        
        buffer = self._create_buffer(text)
        hb.shape(hb_font, buffer)
        
        return self._process_shaped_buffer(buffer, font_size, upem)
    
    def _create_buffer(self, text: str) -> hb.Buffer:
        """Create and configure HarfBuzz buffer for text."""
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        return buffer
    
    def _process_shaped_buffer(
        self, 
        buffer: hb.Buffer, 
        font_size: float, 
        upem: int
    ) -> ShapedText:
        """Convert HarfBuzz buffer results to ShapedText."""
        infos = buffer.glyph_infos
        positions = buffer.glyph_positions
        
        glyphs: list[ShapedGlyph] = []
        total_width = 0.0
        
        for info, pos in zip(infos, positions):
            glyph = self._create_shaped_glyph(info, pos, font_size, upem)
            glyphs.append(glyph)
            total_width += glyph.x_advance
        
        return ShapedText(glyphs=glyphs, width=total_width)
    
    def _create_shaped_glyph(
        self,
        info,
        pos,
        font_size: float,
        upem: int
    ) -> ShapedGlyph:
        """Convert HarfBuzz font units to points."""
        scale_factor = font_size / upem
        
        return ShapedGlyph(
            glyph_id=info.codepoint,
            x_advance=pos.x_advance * scale_factor,
            y_advance=pos.y_advance * scale_factor,
            x_offset=pos.x_offset * scale_factor,
            y_offset=pos.y_offset * scale_factor
        )
    
    def _get_or_create_hb_font(self, font: skia.Font) -> tuple[hb.Font, int]:
        """Get cached HarfBuzz font or create new one."""
        typeface = font.getTypeface()
        font_size = font.getSize()
        cache_key = (id(typeface), font_size)
        
        if cache_key in self._font_cache:
            hb_font, upem, _ = self._font_cache[cache_key]
            return hb_font, upem
        
        return self._create_and_cache_hb_font(typeface, cache_key)
    
    def _create_and_cache_hb_font(
        self,
        typeface: skia.Typeface,
        cache_key: tuple[int, float]
    ) -> tuple[hb.Font, int]:
        """Create HarfBuzz font from Skia typeface and cache it."""
        table_loader = SkiaTableLoader(typeface)
        hb_face = hb.Face.create_for_tables(table_loader.get_table, None)
        hb_font = hb.Font(hb_face)
        
        upem = hb_face.upem
        hb_font.scale = (upem, upem)
        
        self._font_cache[cache_key] = (hb_font, upem, table_loader)
        return hb_font, upem
