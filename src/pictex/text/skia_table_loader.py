"""
Font table loader for HarfBuzz integration with Skia typefaces.

This module provides a component for loading font tables from Skia
typefaces into HarfBuzz.
"""
from typing import Optional
import skia


class SkiaTableLoader:
    """
    Loads and caches font tables from Skia typefaces for HarfBuzz.
    
    This class serves as a callback for HarfBuzz's create_for_tables() method,
    providing font table data on demand while maintaining references to prevent
    garbage collection issues.
    
    The cache prevents Python's GC from freeing table data while
    HarfBuzz still holds pointers to it, avoiding Use-After-Free bugs that
    cause non-deterministic behavior.
    """
    
    def __init__(self, typeface: skia.Typeface):
        self.typeface = typeface
        self._table_cache: dict[int, bytes] = {}
    
    def get_table(self, face, tag_str, user_data):
        """
        Callback for HarfBuzz to request font table data.
        
        Args:
            face: HarfBuzz face (unused)
            tag_str: Table tag as string (e.g., "head", "GSUB")
            user_data: User data (unused)
        
        Returns:
            bytes of table data, or None if table doesn't exist
        """
        tag_int = self._parse_tag(tag_str)
        if tag_int is None:
            return None
        
        if tag_int in self._table_cache:
            return self._table_cache[tag_int]
        
        table_data = self._load_table(tag_int)
        if table_data is None:
            return None
        
        self._table_cache[tag_int] = table_data
        return table_data
    
    def _parse_tag(self, tag_str) -> Optional[int]:
        """Convert tag string to integer (e.g., 'head' -> 0x68656164)."""
        try:
            return int.from_bytes(tag_str.encode('ascii'), 'big')
        except (UnicodeEncodeError, AttributeError):
            return None
    
    def _load_table(self, tag_int: int) -> Optional[bytes]:
        """Load table data from Skia typeface."""
        data = self.typeface.getTableData(tag_int)
        if not data:
            return None
        return bytes(data)
