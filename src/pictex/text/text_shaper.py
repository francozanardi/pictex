import skia
from typing import List
from .typeface_loader import TypefaceLoader
from .font_manager import FontManager
from ..models import Style, Line, TextRun

class TextShaper:
    def __init__(self, style: Style, font_manager: FontManager):
        self._style = style
        self._font_manager = font_manager

    def shape(self, text: str) -> List[Line]:
        """
        Breaks a text string into lines and runs, applying font fallbacks.
        This is the core of the text shaping and fallback logic.
        """

        shaped_lines: list[Line] = []
        font_height = self._get_primary_font_height()
        for line_text in text.split('\n'):
            if not line_text:
                shaped_lines.append(self._create_empty_line())
                continue
            
            runs: list[TextRun] = self._split_line_in_runs(line_text)
            line = self._create_line(runs, font_height)
            shaped_lines.append(line)
        
        return shaped_lines

    def _get_primary_font_height(self) -> float:
        font_metrics = self._font_manager.get_primary_font().getMetrics()
        return -font_metrics.fAscent + font_metrics.fDescent + font_metrics.fLeading

    def _create_empty_line(self) -> Line:
        """Handle empty lines by creating a placeholder with correct height"""

        primary_font = self._font_manager.get_primary_font()
        line = Line(runs=[], width=0, bounds=skia.Rect.MakeEmpty())
        font_metrics = primary_font.getMetrics()
        line.bounds = skia.Rect.MakeLTRB(0, font_metrics.fAscent, 0, font_metrics.fDescent)
        return line
    
    def _create_line(self, runs: list[TextRun], font_height: float) -> Line:
        line_width = 0
        for run in runs:
            run.width = run.font.measureText(run.text)
            line_width += run.width

        return Line(runs=runs, width=line_width, height=font_height, bounds=skia.Rect.MakeWH(line_width, font_height))
    
    def _split_line_in_runs(self, line_text: str) -> list[TextRun]:
        primary_font = self._font_manager.get_primary_font()
        line_runs: list[TextRun] = []
        current_run_text = ""

        for char in line_text:
            if self._is_glyph_supported_for_typeface(char, primary_font.getTypeface()):
                current_run_text += char
                continue

            if current_run_text:
                run = TextRun(current_run_text, primary_font)
                line_runs.append(run)
                current_run_text = ""

            fallback_font = self._get_fallback_font_for_glyph(char, primary_font)
            is_same_font_than_last_run = len(line_runs) > 0 and line_runs[-1].font.getTypeface() == fallback_font.getTypeface()
            if is_same_font_than_last_run:
                # we join contiguous runs with same font
                line_runs[-1] = TextRun(line_runs[-1].text + char, fallback_font)
            else:
                line_runs.append(TextRun(char, fallback_font))
        
        # Add the last run
        if current_run_text:
            run = TextRun(current_run_text, primary_font)
            line_runs.append(run)
        
        return line_runs

    def _get_fallback_font_for_glyph(self, glyph: str, primary_font: skia.Font) -> skia.Font:
        fallback_typefaces = self._font_manager.get_fallback_font_typefaces()
        for typeface in fallback_typefaces:
            if self._is_glyph_supported_for_typeface(glyph, typeface):
                fallback_font = primary_font.makeWithSize(primary_font.getSize())
                fallback_font.setTypeface(typeface)
                return fallback_font

        # if we don't find a font supporting the glyph, we try to find one in the system
        font_style = skia.FontStyle(
            weight=self._style.font_weight.get(),
            width=skia.FontStyle.kNormal_Width,
            slant=self._style.font_style.get().to_skia_slant()
        )
        system_typeface = TypefaceLoader.load_for_glyph(glyph, font_style)
        if system_typeface:
            fallback_font = primary_font.makeWithSize(primary_font.getSize())
            fallback_font.setTypeface(system_typeface)
            return fallback_font

        # if we don't find any font in the system supporting the glyph, we just use the primary font
        return primary_font

    def _is_glyph_supported_for_typeface(self, glyph: str, typeface: skia.Typeface) -> bool:
        return typeface.unicharToGlyph(ord(glyph)) != 0
    