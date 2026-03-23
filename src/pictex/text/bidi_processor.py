"""
BiDi (Bidirectional) text processing using python-bidi library.

This module provides utilities to analyze and reorder text according to 
the Unicode Bidirectional Algorithm (UAX #9), which is essential for proper
rendering of mixed LTR/RTL text.
"""
from typing import Optional
from ..models import BiDiFragment, TextDirection


class BiDiProcessor:
    """
    Processes text using the Unicode BiDi algorithm.
    
    The BiDi algorithm determines the correct visual order for text that
    contains both LTR and RTL runs (e.g., English + Arabic).
    """
    
    def get_bidi_fragments(self, text: str, base_direction: Optional[TextDirection] = None) -> list[BiDiFragment]:
        """
        Apply BiDi algorithm to split text into uniform-direction fragments,
        sorted in their final visual order (Left-to-Right layout sequence).
        
        Args:
            text: The input logical text to process
            base_direction: The base paragraph direction (LTR or RTL).
                            If None, the algorithm auto-detects from the text.
        
        Returns:
            A list of BiDiFragment objects representing the logical text 
            chunks sorted dynamically for LTR physical drawing.
        """
        if not text:
            return []
        
        if base_direction == TextDirection.RTL:
            base_level = 'R'
        elif base_direction == TextDirection.LTR:
            base_level = 'L'
        else:
            base_level = None
        
        return self._get_fragments_with_preserved_joiners(text, base_level)

    def _get_fragments_with_preserved_joiners(self, text: str, base_level: Optional[str]) -> list[BiDiFragment]:
        """
        Process text with bidi algorithm to get visual fragments while preserving ZWJ and ZWNJ.
        """
        temp_text, replacements = self._hide_joiners(text)
        
        # We unroll `bidi.algorithm.get_display()` here to intercept the algorithmic `storage`
        # halfway through (right after mirroring but before it gets flattened into a string).
        storage = self._run_bidi_pipeline(temp_text, base_level)
        
        visual_fragments = self._extract_fragments_from_storage(temp_text, storage)
        
        self._restore_joiners(visual_fragments, replacements)
        return visual_fragments

    def _hide_joiners(self, text: str) -> tuple[str, list[tuple[str, str]]]:
        """Temporarily mask ZWJ and ZWNJ with Private Use Area chars to survive BiDi processing."""
        replacements: list[tuple[str, str]] = []
        chars_to_preserve = ['\u200d', '\u200c']
        temp_text = text
        pua_code = 0xE000
        
        for char in chars_to_preserve:
            if char in temp_text:
                while chr(pua_code) in temp_text:
                    pua_code += 1
                    if pua_code > 0xF8FF:
                        break
                
                if pua_code <= 0xF8FF:
                    pua_char = chr(pua_code)
                    temp_text = temp_text.replace(char, pua_char)
                    replacements.append((pua_char, char))
                    pua_code += 1
                    
        return temp_text, replacements

    def _run_bidi_pipeline(self, text: str, base_level: Optional[str]) -> dict:
        """
        Executes the sequential Unicode BiDi Algorithm steps exactly as `bidi.algorithm.get_display()` does.
        By calling these steps manually, we retain access to the internal `storage` dictionary,
        which contains the exact physical layout positions and resolving levels.
        """
        from bidi.algorithm import (
            get_empty_storage, get_base_level, get_embedding_levels,
            explicit_embed_and_overrides, resolve_weak_types,
            resolve_neutral_types, resolve_implicit_levels,
            reorder_resolved_levels, apply_mirroring
        )
        
        storage = get_empty_storage()
        storage["base_level"] = get_base_level(text, upper_is_rtl=False) if base_level is None else (1 if base_level == "R" else 0)
        storage["base_dir"] = ("L", "R")[storage["base_level"]]
        
        # 1. Determine embedding levels for each logical character
        get_embedding_levels(text, storage, upper_is_rtl=False, debug=False)
        
        # 2. Resolve embedding boundaries and contextual overrides
        explicit_embed_and_overrides(storage, debug=False)
        resolve_weak_types(storage, debug=False)
        resolve_neutral_types(storage, debug=False)
        resolve_implicit_levels(storage, debug=False)
        
        # We inject original logical index tracking before characters are visually shuffled
        for i, ch in enumerate(storage["chars"]):
            ch["idx"] = i
            
        # 3. Physically reorder the characters list into Left-to-Right visual display sequence
        reorder_resolved_levels(storage, debug=False)
        apply_mirroring(storage, debug=False)
        
        return storage

    def _extract_fragments_from_storage(self, original_text: str, storage: dict) -> list[BiDiFragment]:
        """
        Groups characters with the same BiDi embedding level into contiguous `BiDiFragment`s.
        Because `storage['chars']` is visually ordered, the returned list is in Left-To-Right sequence.
        """
        fragments: list[BiDiFragment] = []
        if not storage["chars"]:
            return fragments
            
        current_level = storage["chars"][0]["level"]
        run_indices: list[int] = []
        
        for ch in storage["chars"]:
            if ch["level"] != current_level:
                fragments.append(self._create_fragment(original_text, run_indices, current_level))
                current_level = ch["level"]
                run_indices = []
            run_indices.append(ch["idx"])
            
        if run_indices:
            fragments.append(self._create_fragment(original_text, run_indices, current_level))
            
        return fragments

    def _create_fragment(self, text: str, indices: list[int], level: int) -> BiDiFragment:
        min_idx = min(indices)
        max_idx = max(indices)
        frag_text = text[min_idx:max_idx+1]
        
        # Even layers are LTR, odd layers are RTL
        direction = TextDirection.RTL if level % 2 != 0 else TextDirection.LTR
        return BiDiFragment(text=frag_text, direction=direction, start_index=min_idx)

    def _restore_joiners(self, fragments: list[BiDiFragment], replacements: list[tuple[str, str]]) -> None:
        """Restores PUA characters back to their original ZWJ/ZWNJ characters."""
        for fragment in fragments:
            for pua_char, original_char in replacements:
                fragment.text = fragment.text.replace(pua_char, original_char)
