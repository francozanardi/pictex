"""
BiDi (Bidirectional) text processing using python-bidi library.

This module provides utilities to analyze and reorder text according to 
the Unicode Bidirectional Algorithm (UAX #9), which is essential for proper
rendering of mixed LTR/RTL text.
"""
from typing import NamedTuple, Optional
from ..models.public.text_direction import TextDirection


class BiDiRun(NamedTuple):
    """A segment of text with uniform direction."""
    text: str
    start: int  # Start position in original string
    end: int    # End position in original string
    level: int  # BiDi embedding level (even = LTR, odd = RTL)


class BiDiProcessor:
    """
    Processes text using the Unicode BiDi algorithm.
    
    The BiDi algorithm determines the correct visual order for text that
    contains both LTR and RTL runs (e.g., English + Arabic).
    """
    
    def process(self, text: str, base_direction: Optional[TextDirection] = None) -> str:
        """
        Apply BiDi algorithm to reorder text for visual display.
        
        Args:
            text: The input text to process
            base_direction: The base paragraph direction (LTR or RTL).
                           If None, the algorithm auto-detects from the text.
        
        Returns:
            The visually reordered text ready for rendering
        
        Example:
            >>> processor = BiDiProcessor()
            >>> # Mixed English and Arabic
            >>> text = "Hello مرحبا World"
            >>> result = processor.process(text)
            >>> # Arabic word is now visually reversed
        """
        if not text:
            return text
        
        if base_direction == TextDirection.RTL:
            base_level = 'R'
        elif base_direction == TextDirection.LTR:
            base_level = 'L'
        else:
            base_level = None
        
        # NOTE: We are intentionally using the pure Python implementation (`bidi.algorithm.get_display`)
        # instead of the Rust-backed one (`bidi.get_display`).
        #
        # Although the Rust implementation correctly preserves ZWJ and ZWNJ characters (essential for emojis),
        # it fails to correctly handle character mirroring (e.g., parentheses in RTL contexts).
        # For example, "العربية (RTL Override)" renders with inverted parentheses in the Rust version.
        #
        # To get the best of both worlds (correct structure/mirroring from Python + correct emojis),
        # we use the Python implementation but manually patch the ZWJ/ZWNJ stripping issue
        # by temporarily replacing them with safe Private Use Area (PUA) characters.
        
        return self._process_with_preserved_joiners(text, base_level)

    def _process_with_preserved_joiners(self, text: str, base_level: Optional[str]) -> str:
        """
        Process text with `bidi.algorithm.get_display` while preserving ZWJ and ZWNJ.
        
        The python-bidi library strips "Boundary Neutral" characters like:
        - ZWJ (Zero Width Joiner, \u200d) -> Breaks complex emojis
        - ZWNJ (Zero Width Non-Joiner, \u200c) -> Breaks ligatures (e.g. Persian/Farsi)
        
        This method replaces them with PUA characters before processing and restores them after.
        """
        from bidi.algorithm import get_display

        replacements = []
        chars_to_preserve = ['\u200d', '\u200c']
        
        temp_text = text
        pua_code = 0xE000
        
        for char in chars_to_preserve:
            if char in temp_text:
                # Find a safe PUA char range that isn't used in the text
                while chr(pua_code) in temp_text:
                    pua_code += 1
                    if pua_code > 0xF8FF:
                        # Fallback if no PUA available (extremely unlikely)
                        break
                
                if pua_code <= 0xF8FF:
                    pua_char = chr(pua_code)
                    temp_text = temp_text.replace(char, pua_char)
                    replacements.append((pua_char, char))
                    pua_code += 1

        processed = get_display(temp_text, base_dir=base_level)
        
        # Restore characters
        for pua_char, original_char in replacements:
            processed = processed.replace(pua_char, original_char)
            
        return processed

