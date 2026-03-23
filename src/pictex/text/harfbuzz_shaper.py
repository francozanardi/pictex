import skia
import uharfbuzz as hb
from typing import NamedTuple, Optional
from dataclasses import dataclass
from .skia_table_loader import SkiaTableLoader
from ..models.public.text_direction import TextDirection


@dataclass
class ShapedGlyph:
    """A single shaped glyph with positioning information in points."""
    glyph_id: int
    cluster: int
    x_advance: float
    y_advance: float
    x_offset: float
    y_offset: float


class ShapedText(NamedTuple):
    """Result of HarfBuzz text shaping."""
    glyphs: list[ShapedGlyph]
    width: float
    visual_width: float  # Includes last glyph overhang (e.g. italic slant)


class HarfBuzzShaper:
    """
    Shapes text using HarfBuzz for accurate glyph positioning.
    
    Maintains a cache of HarfBuzz fonts to avoid repeatedly loading
    the same font data. For system fonts, keeps table loaders alive
    to prevent garbage collection issues.
    """
    
    def __init__(self) -> None:
        self._font_cache: dict[tuple[int, float], tuple[hb.Font, int, object]] = {}
    
    def shape(self, text: str, font: skia.Font, direction: TextDirection = TextDirection.LTR) -> ShapedText:
        """
        Shape text using HarfBuzz.
        
        Args:
            text: The text to shape
            font: The Skia font to use for shaping
            direction: The logical direction of the text
        
        Returns:
            ShapedText with glyphs and total width
        """
        hb_font, upem = self._get_or_create_hb_font(font)
        font_size = font.getSize()
        
        buffer = self._create_buffer(text, direction)
        hb.shape(hb_font, buffer)
        
        return self._process_shaped_buffer(buffer, hb_font, font_size, upem, direction)
    
    def _create_buffer(self, text: str, direction: TextDirection) -> hb.Buffer:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        buffer.direction = direction.value
        return buffer
    
    def _process_shaped_buffer(
        self, 
        buffer: hb.Buffer,
        hb_font: hb.Font,
        font_size: float, 
        upem: int,
        direction: TextDirection
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
        
        visual_width = self._compute_visual_width(glyphs, hb_font, font_size, upem, direction)
        
        return ShapedText(glyphs=glyphs, width=total_width, visual_width=visual_width)
    
    def _create_shaped_glyph(
        self,
        info,
        pos,
        font_size: float,
        upem: int
    ) -> ShapedGlyph:
        """Convert HarfBuzz font units to points.

        Uses (value * font_size) / upem instead of value * (font_size / upem)
        to minimize floating-point error. The former keeps intermediate products
        as exact integers (font units * font size) before a single division,
        while the latter pre-divides and accumulates rounding error per glyph.
        """
        return ShapedGlyph(
            glyph_id=info.codepoint,
            cluster=info.cluster,
            x_advance=(pos.x_advance * font_size) / upem,
            y_advance=(pos.y_advance * font_size) / upem,
            x_offset=(pos.x_offset * font_size) / upem,
            y_offset=(pos.y_offset * font_size) / upem,
        )
    
    def _compute_visual_width(
        self,
        glyphs: list[ShapedGlyph],
        hb_font: hb.Font,
        font_size: float,
        upem: int,
        direction: TextDirection
    ) -> float:
        """Compute visual width accounting for overhang."""
        if not glyphs:
            return 0.0
        
        advance_width = sum(g.x_advance for g in glyphs)
        
        last_glyph = glyphs[0] if direction == TextDirection.RTL else glyphs[-1]
        extents = hb_font.get_glyph_extents(last_glyph.glyph_id)
        if extents is None:
            return advance_width
        
        last_glyph_x = advance_width - last_glyph.x_advance + last_glyph.x_offset
        visual_right = last_glyph_x + ((extents.x_bearing + extents.width) * font_size) / upem
        
        return max(advance_width, visual_right)
    
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
        
        self._apply_font_variations(hb_font, typeface)
        
        self._font_cache[cache_key] = (hb_font, upem, table_loader)
        return hb_font, upem
    
    def _apply_font_variations(self, hb_font: hb.Font, typeface: skia.Typeface) -> None:
        """Apply variable font variations to HarfBuzz font."""
        try:
            params = typeface.getVariationDesignParameters()
            if not params:
                return
            
            coords = typeface.getVariationDesignPosition()
            if not coords:
                return
            
            variations = {}
            for coord in coords:
                tag_bytes = coord.axis.to_bytes(4, 'big')
                tag_str = tag_bytes.decode('ascii', errors='ignore').strip()
                if tag_str:
                    variations[tag_str] = coord.value
            
            if variations:
                hb_font.set_variations(variations)
        except (AttributeError, Exception):
            pass
