"""
BiDi (Bidirectional) text processing using python-bidi library.

This module provides utilities to analyze and reorder text according to 
the Unicode Bidirectional Algorithm (UAX #9), which is essential for proper
rendering of mixed LTR/RTL text.
"""
from typing import NamedTuple, Optional
from bidi.algorithm import get_display
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
        
        return get_display(text, base_dir=base_level)

