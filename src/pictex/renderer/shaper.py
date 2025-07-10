# src/pictex/renderer/shaper.py
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
        
        primary_font = self._font_manager.get_primary_font()
        fallback_typefaces = self._font_manager.get_fallback_font_typefaces()
        
        shaped_lines: list[Line] = []
        for line_text in text.split('\n'):
            if not line_text:
                # Handle empty lines by creating a placeholder with correct height
                line = Line(runs=[], width=0, bounds=skia.Rect.MakeEmpty())
                font_metrics = primary_font.getMetrics()
                line.bounds = skia.Rect.MakeLTRB(0, font_metrics.fAscent, 0, font_metrics.fDescent)
                shaped_lines.append(line)
                continue

            current_run_text = ""
            current_font = primary_font
            line_runs: list[TextRun] = []

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
                
                if not found_fallback:
                    current_font = primary_font

                # If no fallback supports it, revert to the primary font
                # which will render the '.notdef' (e.g., '□') glyph.
                current_run_text = char
            
            # Add the last run
            if current_run_text:
                run = TextRun(current_run_text, current_font)
                line_runs.append(run)

            # Calculate widths for the completed line
            line_width = 0
            line_bounds = skia.Rect.MakeEmpty()
            for run in line_runs:
                run.width = run.font.measureText(run.text)
                run_bounds = skia.Rect()
                run.font.measureText(run.text, bounds=run_bounds)
                run_bounds.offset(line_width, 0)
                line_bounds.join(run_bounds)
                line_width += run.width

            shaped_lines.append(Line(runs=line_runs, width=line_width, bounds=line_bounds))
            
        return shaped_lines
