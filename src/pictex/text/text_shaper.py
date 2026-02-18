import skia
from typing import List, Optional
from .typeface_loader import TypefaceLoader
from .font_manager import FontManager
from .harfbuzz_shaper import HarfBuzzShaper, ShapedGlyph
from ..models import Style, Line, TextRun
from .bidi_processor import BiDiProcessor
from .. import utils
import re
import regex

class TextShaper:
    def __init__(self, style: Style, font_manager: FontManager):
        self._style = style
        self._font_manager = font_manager
        self._hb_shaper = HarfBuzzShaper()
        self._bidi_processor = BiDiProcessor()

    def shape(self, text: str, max_width: Optional[float] = None) -> List[Line]:
        """
        Breaks a text string into lines and runs, applying font fallbacks.
        This is the core of the text shaping and fallback logic.
        If max_width is provided, performs word wrapping.
        """

        shaped_lines: list[Line] = []
        
        for line_text in text.split('\n'):
            if not line_text:
                shaped_lines.append(self._create_empty_line())
                continue
            
            direction = self._style.direction.get()
            visual_text = self._bidi_processor.process(line_text, direction)
            if max_width is not None:
                wrapped_lines = self._wrap_line_to_width(visual_text, max_width)
                for wrapped_line_text in wrapped_lines:
                    if not wrapped_line_text:
                        shaped_lines.append(self._create_empty_line())
                        continue
                    wrapped_runs: list[TextRun] = self._split_line_in_runs(wrapped_line_text)
                    line = self._create_line(wrapped_runs)
                    shaped_lines.append(line)
            else:
                runs: list[TextRun] = self._split_line_in_runs(visual_text)
                line = self._create_line(runs)
                shaped_lines.append(line)
        
        return shaped_lines

    def _create_empty_line(self) -> Line:
        """Handle empty lines by creating a placeholder with correct height"""

        primary_font = self._font_manager.get_primary_font()
        line = Line(runs=[], height=0, width=0, bounds=skia.Rect.MakeEmpty())
        font_metrics = primary_font.getMetrics()
        line.bounds = skia.Rect.MakeLTRB(0, font_metrics.fAscent, 0, font_metrics.fDescent)
        return line
    
    def _create_line(self, runs: list[TextRun]) -> Line:
        line_width = 0.0
        font_height = 0.0
        last_visual_width = 0.0
        
        # Calculate common baseline for entire line from primary font
        # This ensures all runs are vertically aligned regardless of fallback fonts
        primary_font = self._font_manager.get_primary_font()
        common_baseline = self._calculate_baseline_offset(primary_font)
        
        for run in runs:
            last_visual_width = self._shape_and_create_blob(run, common_baseline)
            line_width += run.width
            font_height = max(font_height, self._font_manager.get_font_height(run.font))

        # Use visual_width for the last run to capture italic overhang
        bounds_width = line_width - runs[-1].width + last_visual_width if runs else line_width

        return Line(
            runs=runs,
            width=line_width,
            height=font_height,
            bounds=skia.Rect.MakeWH(bounds_width, font_height)
        )
    
    def _shape_and_create_blob(self, run: TextRun, baseline_y: float) -> float:
        """Shape a text run and create its blob. Returns the visual width."""
        shaped = self._hb_shaper.shape(run.text, run.font)
        run.width = shaped.width
        
        if shaped.glyphs:
            run.blob = self._create_text_blob(shaped.glyphs, run.font, baseline_y)
        else:
            run.blob = None
        
        return shaped.visual_width
    
    def _create_text_blob(self, glyphs: list, font: skia.Font, baseline_y: float) -> skia.TextBlob:
        import struct
        
        glyph_data = b''.join(
            struct.pack('<H', g.glyph_id) for g in glyphs
        )
        positions = self._calculate_glyph_positions_with_offsets(glyphs, baseline_y)
        
        return skia.TextBlob.MakeFromPosText(
            glyph_data,
            positions,
            font=font,
            encoding=skia.TextEncoding.kGlyphID
        )
    
    
    def _calculate_glyph_positions_with_offsets(self, glyphs: list, baseline_y: float) -> list[tuple[float, float]]:
        """Calculate (x, y) positions for each glyph, applying HarfBuzz offsets.
        
        Args:
            glyphs: List of shaped glyphs from HarfBuzz
            baseline_y: Common baseline Y position for the entire line
        """
        positions = []
        current_x = 0.0
        
        for glyph in glyphs:
            x = current_x + glyph.x_offset
            y = baseline_y + glyph.y_offset
            positions.append((x, y))
            current_x += glyph.x_advance
        
        return positions
    
    def _calculate_baseline_offset(self, font: skia.Font) -> float:
        metrics = font.getMetrics()
        return -metrics.fAscent
    
    def _split_line_in_runs(self, line_text: str) -> list[TextRun]:
        primary_font = self._font_manager.get_primary_font()
        line_runs: list[TextRun] = []
        current_run_text = ""

        for grapheme in regex.findall(r"\X", line_text):
            if utils.is_grapheme_supported_for_typeface(grapheme, primary_font.getTypeface()):
                current_run_text += grapheme
                continue

            if current_run_text:
                run = TextRun(current_run_text, primary_font)
                line_runs.append(run)
                current_run_text = ""

            fallback_font = self._get_fallback_font_for_glyph(grapheme, primary_font)
            is_same_font_than_last_run = len(line_runs) > 0 and line_runs[-1].font.getTypeface() == fallback_font.getTypeface()
            if is_same_font_than_last_run:
                # we join contiguous runs with same font
                line_runs[-1] = TextRun(line_runs[-1].text + grapheme, fallback_font)
            else:
                line_runs.append(TextRun(grapheme, fallback_font))
        
        # Add the last run
        if current_run_text:
            run = TextRun(current_run_text, primary_font)
            line_runs.append(run)
        
        return line_runs

    def _get_fallback_font_for_glyph(self, grapheme: str, primary_font: skia.Font) -> skia.Font:
        fallback_typefaces = self._font_manager.get_fallback_font_typefaces()
        for typeface in fallback_typefaces:
            if utils.is_grapheme_supported_for_typeface(grapheme, typeface):
                fallback_font = primary_font.makeWithSize(primary_font.getSize())
                fallback_font.setTypeface(typeface)
                return fallback_font

        # if we don't find a font supporting the grapheme, we try to find one in the system
        font_style = skia.FontStyle(
            weight=self._style.font_weight.get(),
            width=skia.FontStyle.kNormal_Width,
            slant=self._style.font_style.get().to_skia_slant()
        )
        system_typeface = TypefaceLoader.load_for_grapheme(grapheme, font_style)
        if system_typeface:
            fallback_font = primary_font.makeWithSize(primary_font.getSize())
            fallback_font.setTypeface(system_typeface)
            return fallback_font

        # if we don't find any font in the system supporting the glyph, we just use the primary font
        return primary_font

    def _wrap_line_to_width(self, text: str, max_width: float) -> List[str]:
        """
        Wraps a single line of text to fit within the specified width.
        Words are treated as indivisible units.
        
        Token widths are derived by splitting the text into font-fallback
        runs, shaping each run with its actual font, and then mapping
        glyph clusters back to token boundaries. This ensures characters
        that require fallback fonts (e.g. emojis) are measured accurately.
        """
        tokens: list[str] = re.findall(r'\S+|\s+', text)
        if not tokens:
            return ['']

        all_glyphs = self._shape_runs_with_absolute_clusters(text)
        token_widths = self._compute_token_widths_from_shaping(tokens, all_glyphs)

        wrapped_lines: List[str] = []
        current_line_tokens: list[str] = []
        current_width = 0.0

        for i, token in enumerate(tokens):
            token_width = token_widths[i]

            if not current_line_tokens:
                current_line_tokens.append(token)
                current_width = token_width
                continue

            potential_width = current_width + token_width

            # Allow trailing whitespace to hang/overflow
            if potential_width <= max_width or token.isspace():
                current_line_tokens.append(token)
                current_width = potential_width
            else:
                wrapped_lines.append(''.join(current_line_tokens).strip())
                current_line_tokens = [token]
                current_width = token_width

        if current_line_tokens:
            wrapped_lines.append(''.join(current_line_tokens).strip())

        if len(wrapped_lines) == 1:
            # This is to avoid removing spaces at the begining or at the end of a line
            # when the line was not actually wrapped.
            # When the line is wrapped we must remove spaces at the begining and at the end of each line
            # to obtain an useful behavior (avoid single spaces at the begining of a line, for example)
            return [text]
        
        return wrapped_lines if wrapped_lines else ['']

    def _shape_runs_with_absolute_clusters(self, text: str) -> list[ShapedGlyph]:
        """Split text into font-fallback runs, shape each, and return combined glyphs.

        Each run is shaped with its actual font (primary or fallback).
        Cluster values are reindexed to absolute character positions in the
        full text so callers can map glyphs back to token boundaries.
        """
        runs = self._split_line_in_runs(text)
        all_glyphs: list[ShapedGlyph] = []
        char_offset = 0

        for run in runs:
            shaped = self._hb_shaper.shape(run.text, run.font)
            for glyph in shaped.glyphs:
                all_glyphs.append(ShapedGlyph(
                    glyph_id=glyph.glyph_id,
                    cluster=glyph.cluster + char_offset,
                    x_advance=glyph.x_advance,
                    y_advance=glyph.y_advance,
                    x_offset=glyph.x_offset,
                    y_offset=glyph.y_offset,
                ))
            char_offset += len(run.text)

        return all_glyphs

    def _compute_token_widths_from_shaping(
        self, tokens: list[str], glyphs: list
    ) -> list[float]:
        """Compute each token's width from glyph clusters.
        
        Each glyph's cluster value indicates the character position it maps to.
        By matching glyph clusters to token character ranges, the resulting
        widths preserve inter-token kerning and sum exactly to the total width.
        """
        token_widths: list[float] = []
        char_offset = 0

        for token in tokens:
            token_start = char_offset
            token_end = char_offset + len(token)

            width = sum(
                glyph.x_advance
                for glyph in glyphs
                if token_start <= glyph.cluster < token_end
            )

            token_widths.append(width)
            char_offset = token_end

        return token_widths
    