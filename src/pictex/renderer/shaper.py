import skia
from typing import List
from ..models import Style
from .structs import Line, TextRun
from .font_manager import FontManager

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
        for line_text in text.split('\n'):
            if not line_text:
                shaped_lines.append(self._create_empty_line())
                continue
            
            runs: list[TextRun] = self._split_line_in_runs()
            line = self._create_line(runs)
            shaped_lines.append(line)
            
        return shaped_lines

    def _create_empty_line(self) -> Line:
        '''Handle empty lines by creating a placeholder with correct height'''

        primary_font = self._font_manager.get_primary_font()
        line = Line(runs=[], width=0, bounds=skia.Rect.MakeEmpty())
        font_metrics = primary_font.getMetrics()
        line.bounds = skia.Rect.MakeLTRB(0, font_metrics.fAscent, 0, font_metrics.fDescent)
        return line
    
    def _create_line(self, runs: list[TextRun]) -> Line:
        line_width = 0
        line_bounds = skia.Rect.MakeEmpty()
        for run in runs:
            run.width = run.font.measureText(run.text)
            run_bounds = skia.Rect()
            run.font.measureText(run.text, bounds=run_bounds)
            run_bounds.offset(line_width, 0)
            line_bounds.join(run_bounds)
            line_width += run.width

        return Line(runs=runs, width=line_width, bounds=line_bounds)
    
    def _split_line_in_runs(self, line_text: str) -> list[TextRun]:
        primary_font = self._font_manager.get_primary_font()
        fallback_typefaces = self._font_manager.get_fallback_font_typefaces()

        line_runs: list[TextRun] = []
        current_run_text = ""
        current_font = primary_font

        for char in line_text:
            glyph_id = current_font.unicharToGlyph(ord(char))
            
            if glyph_id != 0:
                # Character is supported, continue the current run
                current_run_text += char
                continue

            # Glyph not found in current font
            if current_run_text:
                run = TextRun(current_run_text, current_font)
                line_runs.append(run)
            
            # Find a new font that supports this character
            found_fallback = False
            for typeface in fallback_typefaces:
                if typeface.unicharToGlyph(ord(char)) != 0:
                    # Found a fallback!
                    current_font = primary_font.makeWithSize(primary_font.getSize())
                    current_font.setTypeface(typeface)
                    found_fallback = True
                    break

            # If no fallback supports it, revert to the primary font
            # which will render the '.notdef' (e.g., '□') glyph.                
            if not found_fallback:
                current_font = primary_font

            current_run_text = char
        
        # Add the last run
        if current_run_text:
            run = TextRun(current_run_text, current_font)
            line_runs.append(run)
        
        return line_runs
