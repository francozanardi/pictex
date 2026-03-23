import skia
from typing import List, Optional
from .typeface_loader import TypefaceLoader
from .font_manager import FontManager
from .harfbuzz_shaper import HarfBuzzShaper, ShapedGlyph
from ..models import Style, Line, TextRun, FontMetrics, TextDirection, BiDiFragment
from .bidi_processor import BiDiProcessor
from .. import utils
import regex

_CJK_PROPS = (
    r'\p{Script=Han}'
    r'\p{Script=Hiragana}'
    r'\p{Script=Katakana}'
    r'\p{Script=Hangul}'
    r'\p{Block=CJK_Symbols_And_Punctuation}'
    r'\p{Block=Halfwidth_And_Fullwidth_Forms}'
)
_WRAP_TOKEN_PATTERN = regex.compile(
    rf'[{_CJK_PROPS}]'             # Each CJK character is its own breakable token
    rf'|[^\s{_CJK_PROPS}]+'        # Non-CJK, non-whitespace grouped as a word
    r'|\s+'                         # Whitespace grouped together
)


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

        if not text:
            return []

        shaped_lines: list[Line] = []
        
        for line_text in text.split('\n'):
            if not line_text:
                shaped_lines.append(self._create_empty_line())
                continue
            
            if max_width is not None:
                wrapped_lines = self._wrap_line_to_width(line_text, max_width)
            else:
                wrapped_lines = [line_text]
                
            for wrapped_line_text in wrapped_lines:
                if not wrapped_line_text:
                    shaped_lines.append(self._create_empty_line())
                    continue
                
                direction = self._style.direction.get()
                bidi_fragments = self._bidi_processor.get_bidi_fragments(wrapped_line_text, direction)
                
                runs_for_line: list[TextRun] = []
                for fragment in bidi_fragments:
                    text_runs = self._split_bidi_fragment(fragment)
                    
                    if fragment.direction == TextDirection.RTL:
                        text_runs.reverse()
                        
                    runs_for_line.extend(text_runs)
                    
                line = self._create_line(runs_for_line)
                shaped_lines.append(line)
        
        return shaped_lines

    def _create_empty_line(self) -> Line:
        """Handle empty lines by creating a placeholder with correct height"""

        primary_font = self._font_manager.get_primary_font()
        primary_font_metrics = self._font_manager.get_font_metrics(primary_font)
        # We must give some width to the empty line, otherwise the rect bounds will be empty,
        # and it will cause issues when we will try to join the bounds of this line with the bounds of other lines (the result will ignore the empty line).
        # The width doesn't matter, it won't be rendered, but it must be greater than 0 to avoid empty bounds.
        empty_line_rect = skia.Rect.MakeWH(1, self._font_manager.get_font_height(primary_font))
        return Line(
            runs=[],
            height=empty_line_rect.height(),
            width=empty_line_rect.width(),
            bounds=empty_line_rect,
            metrics=primary_font_metrics
        )
    
    def _create_line(self, runs: list[TextRun]) -> Line:
        line_width = 0.0
        last_visual_width = 0.0
        line_metrics = self._calculate_line_metrics(runs)
        line_height = line_metrics.ascent + line_metrics.descent + line_metrics.leading
        
        for run in runs:
            last_visual_width = self._shape_and_create_blob(run, line_metrics.ascent)
            line_width += run.width

        # Use visual_width for the last run to capture italic overhang
        bounds_width = line_width - runs[-1].width + last_visual_width if runs else line_width

        return Line(
            runs=runs,
            width=line_width,
            height=line_height,
            bounds=skia.Rect.MakeWH(bounds_width, line_height),
            metrics=line_metrics
        )
    
    def _calculate_line_metrics(self, runs: list[TextRun]) -> FontMetrics:
        """Calculate line metrics using the text runs."""
        max_ascent = 0.0
        max_descent = 0.0
        max_leading = 0.0
        underline_position = 0.0
        strikeout_position = self._font_manager.get_font_metrics(self._font_manager.get_primary_font()).strikeout_position

        for run in runs:
            font_metrics = self._font_manager.get_font_metrics(run.font)
            max_ascent = max(max_ascent, font_metrics.ascent)
            max_descent = max(max_descent, font_metrics.descent)
            max_leading = max(max_leading, font_metrics.leading)

            if font_metrics.underline_position:
                underline_position = max(underline_position, font_metrics.underline_position)

        return FontMetrics(
            ascent=max_ascent,
            descent=max_descent,
            leading=max_leading,
            underline_position=underline_position,
            strikeout_position=strikeout_position
        )
    
    def _shape_and_create_blob(self, run: TextRun, line_ascent: float) -> float:
        """Shape a text run and create its blob. Returns the visual width."""
        shaped = self._hb_shaper.shape_text_run(run)
        run.width = shaped.width
        
        if shaped.glyphs:
            run.blob = self._create_text_blob(shaped.glyphs, run.font, line_ascent)
        else:
            run.blob = None
        
        return shaped.visual_width
    
    def _create_text_blob(self, glyphs: list, font: skia.Font, line_ascent: float) -> skia.TextBlob:
        import struct
        
        glyph_data = b''.join(
            struct.pack('<H', g.glyph_id) for g in glyphs
        )
        positions = self._calculate_glyph_positions_with_offsets(glyphs, line_ascent)
        
        return skia.TextBlob.MakeFromPosText(
            glyph_data,
            positions,
            font=font,
            encoding=skia.TextEncoding.kGlyphID
        )
    
    def _calculate_glyph_positions_with_offsets(self, glyphs: list, line_ascent: float) -> list[tuple[float, float]]:
        """Calculate (x, y) positions for each glyph, applying HarfBuzz offsets.
        
        Args:
            glyphs: List of shaped glyphs from HarfBuzz
            line_ascent: Ascent value for the line
        """
        positions = []
        current_x = 0.0
        
        for glyph in glyphs:
            x = current_x + glyph.x_offset
            y = line_ascent - glyph.y_offset
            positions.append((x, y))
            current_x += glyph.x_advance
        
        return positions

    def _split_bidi_fragment(self, fragment: BiDiFragment) -> list[TextRun]:
        primary_font = self._font_manager.get_primary_font()
        primary_font_metrics = self._font_manager.get_font_metrics(primary_font)
        line_runs: list[TextRun] = []
        current_run_text = ""
        current_run_start = 0
        char_index = 0

        for grapheme in regex.findall(r"\X", fragment.text):
            if utils.is_grapheme_supported_for_typeface(grapheme, primary_font.getTypeface()):
                current_run_text += grapheme
                char_index += len(grapheme)
                continue

            if current_run_text:
                run = TextRun(current_run_text, primary_font, primary_font_metrics, fragment,
                              fragment_offset=current_run_start)
                line_runs.append(run)
                current_run_text = ""
                current_run_start = char_index

            fallback_font = self._get_fallback_font_for_glyph(grapheme, primary_font)
            fallback_font_metrics = self._font_manager.get_font_metrics(fallback_font)
            is_same_font_than_last_run = len(line_runs) > 0 and line_runs[-1].font.getTypeface() == fallback_font.getTypeface()
            if is_same_font_than_last_run:
                # we join contiguous runs with same font
                line_runs[-1] = TextRun(line_runs[-1].text + grapheme, fallback_font, fallback_font_metrics, fragment,
                                        fragment_offset=line_runs[-1].fragment_offset)
            else:
                line_runs.append(TextRun(grapheme, fallback_font, fallback_font_metrics, fragment,
                                         fragment_offset=current_run_start))
            
            char_index += len(grapheme)
            current_run_start = char_index
        
        # Add the last run
        if current_run_text:
            run = TextRun(current_run_text, primary_font, primary_font_metrics, fragment,
                          fragment_offset=current_run_start)
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
        Words are treated as indivisible units, except for CJK characters
        which are each a valid line break point.

        Token widths are derived by splitting the text into font-fallback
        runs, shaping each run with its actual font, and then mapping
        glyph clusters back to token boundaries. This ensures characters
        that require fallback fonts (e.g. emojis) are measured accurately.
        """
        tokens: list[str] = self._tokenize_for_wrapping(text)
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
        direction = self._style.direction.get()
        bidi_fragments = self._bidi_processor.get_bidi_fragments(text, direction)
        all_glyphs: list[ShapedGlyph] = []

        for fragment in bidi_fragments:
            runs = self._split_bidi_fragment(fragment)
            char_offset = fragment.start_index
            
            for run in runs:
                shaped = self._hb_shaper.shape_text_run(run)
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

    def _tokenize_for_wrapping(self, text: str) -> list[str]:
        """Tokenize text for word wrapping.

        Latin/non-CJK words are kept as indivisible units (break at spaces).
        CJK characters are each their own token (break between any two).
        """
        return _WRAP_TOKEN_PATTERN.findall(text)
    