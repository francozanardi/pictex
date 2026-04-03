import skia
from dataclasses import dataclass
from typing import List, Optional
from .typeface_loader import TypefaceLoader
from .font_manager import FontManager
from .harfbuzz_shaper import HarfBuzzShaper
from .line_metrics import LineMetricsCalculator
from ..models import (
    Style,
    Line,
    TextRun,
    SpanInfo,
    TextDirection,
    BiDiFragment,
    ShapedGlyph,
    LetterSpacing,
    LetterSpacingMode,
    FontSmoothing,
)
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


@dataclass
class ResolvedSpan:
    """A span with its text and fully computed style, plus its position in full_text."""
    text: str
    computed_style: Style
    start: int  # absolute char offset in the concatenated full text
    explicit_style: Optional[Style] = None

    @property
    def end(self) -> int:
        return self.start + len(self.text)


class TextShaper:
    def __init__(
        self,
        resolved_spans: List[ResolvedSpan],
        base_style: Style,
        font_smoothing: FontSmoothing,
    ):
        self._resolved_spans = resolved_spans
        self._base_style = base_style
        self._font_smoothing = font_smoothing
        self._full_text = "".join(s.text for s in resolved_spans)
        self._font_managers = [FontManager(s.computed_style, font_smoothing) for s in resolved_spans]
        self._hb_shaper = HarfBuzzShaper()
        self._bidi_processor = BiDiProcessor()

        # One SpanInfo per resolved span - shared by all runs from that span so
        # painters can group co-span runs by object identity (id(run.span)).
        self._span_infos = [SpanInfo(s.computed_style, s.explicit_style) for s in resolved_spans]

        # Fast lookup: id(SpanInfo) → FontManager
        self._span_to_fm = {
            id(span_info): fm
            for span_info, fm in zip(self._span_infos, self._font_managers)
        }

        # Line metrics use the base (block-level) style for line_height,
        # and the first span's font manager as the primary font reference.
        base_fm = self._font_managers[0] if self._font_managers else FontManager(base_style, font_smoothing)
        self._line_metrics_calculator = LineMetricsCalculator(base_style, base_fm)

    def shape(self, max_width: Optional[float] = None) -> List[Line]:
        """
        Shapes the resolved spans into Lines, applying font fallbacks and BiDi reordering.
        Text is taken from self._full_text (the concatenation of all spans).
        If max_width is provided, performs word wrapping.
        """

        if not self._full_text:
            return []

        shaped_lines: list[Line] = []
        line_start = 0  # abs offset of current '\n'-delimited segment in full_text

        for line_text in self._full_text.split('\n'):
            if not line_text:
                shaped_lines.append(self._create_empty_line())
                line_start += 1
                continue

            if max_width is not None:
                wrapped_lines = self._wrap_line_to_width(line_text, line_start, max_width)
            else:
                wrapped_lines = [(line_text, 0)]

            for (wrapped_line_text, inner_start) in wrapped_lines:
                if not wrapped_line_text:
                    shaped_lines.append(self._create_empty_line())
                    continue

                wrapped_abs_start = line_start + inner_start
                direction = self._base_style.direction.get()
                bidi_fragments = self._bidi_processor.get_bidi_fragments(wrapped_line_text, direction)

                runs_for_line: list[TextRun] = []
                for fragment in bidi_fragments:
                    fragment_abs_start = wrapped_abs_start + fragment.start_index
                    text_runs = self._split_bidi_fragment(fragment, fragment_abs_start)

                    if fragment.direction == TextDirection.RTL:
                        text_runs.reverse()

                    runs_for_line.extend(text_runs)

                line = self._create_line(runs_for_line)
                shaped_lines.append(line)

            line_start += len(line_text) + 1  # +1 for '\n'

        return shaped_lines

    def _get_span_index(self, abs_pos: int) -> int:
        for i, span in enumerate(self._resolved_spans):
            if span.start <= abs_pos < span.end:
                return i
        return len(self._resolved_spans) - 1

    def _get_fm_for_run(self, run: TextRun) -> FontManager:
        return self._span_to_fm.get(id(run.span), self._font_managers[0])

    def _create_empty_line(self) -> Line:
        """Handle empty lines by creating a placeholder with correct height."""
        base_fm = self._font_managers[0] if self._font_managers else FontManager(self._base_style, self._font_smoothing)
        primary_font = base_fm.get_primary_font()
        primary_metrics = base_fm.get_font_metrics(primary_font)
        line_metrics = self._line_metrics_calculator.calculate(runs=[], font_metrics=[primary_metrics])

        # We must give some width to the empty line, otherwise the rect bounds will be empty,
        # and it will cause issues when we will try to join the bounds of this line with the bounds of other lines (the result will ignore the empty line).
        # The width doesn't matter, it won't be rendered, but it must be greater than 0 to avoid empty bounds.
        return Line(
            runs=[],
            height=line_metrics.height,
            width=1,
            bounds=skia.Rect.MakeWH(1, line_metrics.height),
            metrics=line_metrics,
        )

    def _create_line(self, runs: list[TextRun]) -> Line:
        font_metrics = [self._get_fm_for_run(run).get_font_metrics(run.font) for run in runs]
        last_visual_width = self._shape_runs(runs)
        line_metrics = self._line_metrics_calculator.calculate(runs, font_metrics)
        self._create_blobs(runs, line_metrics.baseline)
        line_width = sum(run.width for run in runs)
        bounds_width = line_width - runs[-1].width + last_visual_width if runs else line_width

        return Line(
            runs=runs,
            width=line_width,
            height=line_metrics.height,
            bounds=skia.Rect.MakeWH(bounds_width, line_metrics.height),
            metrics=line_metrics,
        )

    def _shape_runs(self, runs: list[TextRun]) -> float:
        """Shape each run with HarfBuzz. Populates run.shaped_glyphs and run.width.

        Returns the visual width of the last run (used for italic overhang).
        """
        last_visual_width = 0.0
        for run in runs:
            last_visual_width = self._shape_run(run)
        return last_visual_width

    def _shape_run(self, run: TextRun) -> float:
        """Shape a single run. Returns its visual width."""
        letter_spacing = run.style.letter_spacing.get()
        has_letter_spacing = not letter_spacing.is_normal

        shaped = self._hb_shaper.shape_text_run(run, disable_optional_ligatures=has_letter_spacing)
        run.shaped_glyphs = shaped.glyphs
        run.width = shaped.width

        if not has_letter_spacing or not run.shaped_glyphs or shaped.is_cursive_script:
            return shaped.visual_width

        spacing_px = self._resolve_letter_spacing_px(letter_spacing, run)
        if spacing_px is not None:
            n_gaps = self._apply_letter_spacing(run.shaped_glyphs, spacing_px)
            run.width += spacing_px * n_gaps

        return shaped.visual_width

    def _resolve_letter_spacing_px(self, letter_spacing: LetterSpacing, run: TextRun) -> Optional[float]:
        """Convert a LetterSpacing value to pixels for the given run's font."""
        if letter_spacing.mode == LetterSpacingMode.ABSOLUTE:
            return letter_spacing.value

        if letter_spacing.mode == LetterSpacingMode.PERCENT:
            # percentage of the space-character width for this font (same behavior that CSS uses)
            space_width = self._get_space_char_width(run.font)
            if space_width is None:
                return None
            return (letter_spacing.value / 100.0) * space_width

        raise ValueError(f"Unsupported LetterSpacingMode: {letter_spacing.mode}")

    def _get_space_char_width(self, font) -> Optional[float]:
        """Return the advance width of the space character for the given font."""
        glyph_ids = font.textToGlyphs(" ")
        if not glyph_ids:
            return None
        widths = font.getWidths(glyph_ids)
        return widths[0] if widths else None

    def _apply_letter_spacing(self, glyphs: list[ShapedGlyph], spacing_px: float) -> int:
        """Add spacing_px after each grapheme cluster boundary.

        Uses HarfBuzz cluster values to detect boundaries: consecutive glyphs
        sharing the same cluster value belong to the same grapheme cluster (e.g.
        a base glyph + combining mark, or a multi-glyph emoji component).
        Spacing is added to the x_advance of the last glyph in each cluster group,
        except for the final cluster - matching browser behaviour.

        Works correctly for both LTR (clusters non-decreasing) and RTL (clusters
        non-increasing), since HarfBuzz returns glyphs in visual order.

        Returns the number of cluster boundaries where spacing was applied,
        so the caller can update run.width accordingly.
        """
        n_gaps = 0
        for i in range(len(glyphs) - 1):
            if glyphs[i].cluster != glyphs[i + 1].cluster:
                glyphs[i].x_advance += spacing_px
                n_gaps += 1
        return n_gaps

    def _create_blobs(self, runs: list[TextRun], baseline: float) -> None:
        """Create TextBlobs for all runs using the final baseline."""
        for run in runs:
            run.blob = self._create_text_blob(run.shaped_glyphs, run.font, baseline) if run.shaped_glyphs else None

    def _create_text_blob(self, glyphs: list, font: skia.Font, baseline: float) -> skia.TextBlob:
        import struct

        glyph_data = b''.join(
            struct.pack('<H', g.glyph_id) for g in glyphs
        )
        positions = self._calculate_glyph_positions_with_offsets(glyphs, baseline)

        return skia.TextBlob.MakeFromPosText(
            glyph_data,
            positions,
            font=font,
            encoding=skia.TextEncoding.kGlyphID
        )

    def _calculate_glyph_positions_with_offsets(self, glyphs: list, baseline: float) -> list[tuple[float, float]]:
        """Calculate (x, y) positions for each glyph, applying HarfBuzz offsets.

        Args:
            glyphs: List of shaped glyphs from HarfBuzz
            line_ascent: Ascent value for the line
        """
        positions = []
        current_x = 0.0

        for glyph in glyphs:
            x = current_x + glyph.x_offset
            y = baseline - glyph.y_offset
            positions.append((x, y))
            current_x += glyph.x_advance

        return positions

    def _split_bidi_fragment(self, fragment: BiDiFragment, fragment_abs_start: int) -> list[TextRun]:
        """Split a BiDi fragment into TextRuns, respecting span and font-fallback boundaries.

        fragment_abs_start is the absolute character offset of this fragment within
        self._full_text, used to look up which ResolvedSpan each grapheme belongs to
        and therefore which FontManager and Style to use.
        """
        line_runs: list[TextRun] = []
        char_index = 0

        for grapheme in regex.findall(r"\X", fragment.text):
            abs_pos = fragment_abs_start + char_index
            span_idx = self._get_span_index(abs_pos)
            span_info = self._span_infos[span_idx]
            fm = self._font_managers[span_idx]
            primary_font = fm.get_primary_font()

            if utils.is_grapheme_supported_for_typeface(grapheme, primary_font.getTypeface()):
                glyph_font = primary_font
            else:
                glyph_font = self._get_fallback_font_for_glyph(grapheme, primary_font, fm, span_info.computed_style)

            # Extend last run if same span AND same font typeface
            if (
                line_runs
                and line_runs[-1].span is span_info
                and line_runs[-1].font.getTypeface() == glyph_font.getTypeface()
            ):
                last = line_runs[-1]
                line_runs[-1] = TextRun(
                    last.text + grapheme, glyph_font, fragment,
                    span=span_info, fragment_offset=last.fragment_offset,
                )
            else:
                line_runs.append(TextRun(
                    grapheme, glyph_font, fragment,
                    span=span_info, fragment_offset=char_index,
                ))

            char_index += len(grapheme)

        return line_runs

    def _get_fallback_font_for_glyph(
        self,
        grapheme: str,
        primary_font: skia.Font,
        fm: FontManager,
        span_style: Style,
    ) -> skia.Font:
        """Find the best font for a grapheme not supported by primary_font.

        Tries fm's configured fallback typefaces first, then searches the system.
        span_style is used to match font weight and style when querying the system.
        Returns primary_font unchanged if no supporting font is found.
        """
        for typeface in fm.get_fallback_font_typefaces():
            if utils.is_grapheme_supported_for_typeface(grapheme, typeface):
                fallback_font = primary_font.makeWithSize(primary_font.getSize())
                fallback_font.setTypeface(typeface)
                return fallback_font

        # if we don't find a font supporting the grapheme, we try to find one in the system
        font_style = skia.FontStyle(
            weight=span_style.font_weight.get(),
            width=skia.FontStyle.kNormal_Width,
            slant=span_style.font_style.get().to_skia_slant()
        )
        system_typeface = TypefaceLoader.load_for_grapheme(grapheme, font_style)
        if system_typeface:
            fallback_font = primary_font.makeWithSize(primary_font.getSize())
            fallback_font.setTypeface(system_typeface)
            return fallback_font

        # if we don't find any font in the system supporting the glyph, we just use the primary font
        return primary_font

    def _wrap_line_to_width(self, line_text: str, line_abs_start: int, max_width: float) -> List[tuple[str, int]]:
        """
        Wraps a single line of text to fit within the specified width.
        Words are treated as indivisible units, except for CJK characters
        which are each a valid line break point.

        line_abs_start is the absolute character offset of line_text within
        self._full_text, forwarded to shaping so each grapheme maps to the
        correct span and font.

        Token widths are derived by splitting the text into font-fallback
        runs, shaping each run with its actual font, and then mapping
        glyph clusters back to token boundaries. This ensures characters
        that require fallback fonts (e.g. emojis) are measured accurately.

        Returns a list of (stripped_text, inner_start_offset) tuples, where
        inner_start_offset is the character offset of the wrapped line's first
        non-space token relative to line_text. This offset is used by the caller
        to compute the absolute position of each wrapped line in self._full_text.
        """
        tokens: list[str] = self._tokenize_for_wrapping(line_text)
        if not tokens:
            return [('', 0)]

        all_glyphs = self._shape_runs_with_absolute_clusters(line_text, line_abs_start)
        token_widths = self._compute_token_widths_from_shaping(tokens, all_glyphs)

        # Precompute token start offsets within line_text
        token_offsets: list[int] = []
        offset = 0
        for token in tokens:
            token_offsets.append(offset)
            offset += len(token)

        wrapped_lines: List[tuple[str, int]] = []
        current_line_tokens: list[str] = []
        current_indices: list[int] = []
        current_width = 0.0

        for i, token in enumerate(tokens):
            token_width = token_widths[i]

            if not current_line_tokens:
                current_line_tokens.append(token)
                current_indices.append(i)
                current_width = token_width
                continue

            potential_width = current_width + token_width

            # Allow trailing whitespace to hang/overflow
            if potential_width <= max_width or token.isspace():
                current_line_tokens.append(token)
                current_indices.append(i)
                current_width = potential_width
            else:
                wrapped_lines.append(self._flush_line(tokens, current_line_tokens, current_indices, token_offsets))
                current_line_tokens = [token]
                current_indices = [i]
                current_width = token_width

        if current_line_tokens:
            wrapped_lines.append(self._flush_line(tokens, current_line_tokens, current_indices, token_offsets))

        if len(wrapped_lines) == 1:
            # This is to avoid removing spaces at the begining or at the end of a line
            # when the line was not actually wrapped.
            # When the line is wrapped we must remove spaces at the begining and at the end of each line
            # to obtain an useful behavior (avoid single spaces at the begining of a line, for example)
            return [(line_text, 0)]

        return wrapped_lines if wrapped_lines else [('', 0)]

    def _flush_line(
        self,
        tokens: list[str],
        current_tokens: list[str],
        current_indices: list[int],
        token_offsets: list[int],
    ) -> tuple[str, int]:
        """Build a (stripped_text, inner_start_offset) tuple for a completed wrapped line.

        inner_start_offset points to the first non-space token in the line,
        so the caller can compute the absolute position of this line in self._full_text.
        """
        stripped = ''.join(current_tokens).strip()
        first_non_space = next(
            (idx for idx in current_indices if not tokens[idx].isspace()),
            current_indices[0],
        )
        return (stripped, token_offsets[first_non_space])

    def _shape_runs_with_absolute_clusters(self, line_text: str, line_abs_start: int) -> list[ShapedGlyph]:
        """Shape all characters in line_text and return the combined glyph list.

        line_abs_start is forwarded to _split_bidi_fragment so each grapheme
        resolves to the correct span and font.

        Each run is shaped with its actual font (primary or fallback).
        Glyph cluster values are kept relative to line_text (not self._full_text)
        so _compute_token_widths_from_shaping can map them to token boundaries.
        """
        direction = self._base_style.direction.get()
        bidi_fragments = self._bidi_processor.get_bidi_fragments(line_text, direction)
        all_glyphs: list[ShapedGlyph] = []

        for fragment in bidi_fragments:
            fragment_abs_start = line_abs_start + fragment.start_index
            runs = self._split_bidi_fragment(fragment, fragment_abs_start)
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
