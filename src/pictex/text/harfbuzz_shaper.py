import skia
import uharfbuzz as hb
from typing import NamedTuple
from dataclasses import dataclass
from .skia_table_loader import SkiaTableLoader


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
        
        return self._process_shaped_buffer(buffer, hb_font, font_size, upem)
    
    def _create_buffer(self, text: str) -> hb.Buffer:
        """Create and configure HarfBuzz buffer for text."""
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        return buffer
    
    def _process_shaped_buffer(
        self, 
        buffer: hb.Buffer,
        hb_font: hb.Font,
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
        
        visual_width = self._compute_visual_width(glyphs, hb_font, font_size, upem)
        
        return ShapedText(glyphs=glyphs, width=total_width, visual_width=visual_width)
    
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
            cluster=info.cluster,
            x_advance=pos.x_advance * scale_factor,
            y_advance=pos.y_advance * scale_factor,
            x_offset=pos.x_offset * scale_factor,
            y_offset=pos.y_offset * scale_factor
        )
    
    def _compute_visual_width(
        self,
        glyphs: list[ShapedGlyph],
        hb_font: hb.Font,
        font_size: float,
        upem: int
    ) -> float:
        """Compute visual width accounting for last glyph overhang.
        
        For italic fonts the last glyph often extends visually beyond its
        advance width. This method checks the actual glyph extents of the
        last glyph to capture that overhang.
        """
        if not glyphs:
            return 0.0
        
        advance_width = sum(g.x_advance for g in glyphs)
        
        last_glyph = glyphs[-1]
        extents = hb_font.get_glyph_extents(last_glyph.glyph_id)
        if extents is None:
            return advance_width
        
        scale_factor = font_size / upem
        
        # Position of the last glyph's origin
        last_glyph_x = advance_width - last_glyph.x_advance + last_glyph.x_offset
        
        # Visual right edge = glyph origin + bearing + width (all in points)
        visual_right = last_glyph_x + (extents.x_bearing + extents.width) * scale_factor
        
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
