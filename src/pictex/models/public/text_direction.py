from enum import Enum


class TextDirection(str, Enum):
    """
    Text direction for horizontal text flow.
    
    Corresponds to CSS `direction` property.
    """
    LTR = "ltr"  # Left-to-right (default)
    RTL = "rtl"  # Right-to-left
    
    def __str__(self) -> str:
        return self.value
