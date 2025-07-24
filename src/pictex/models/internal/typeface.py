from dataclasses import dataclass
import skia
from enum import Enum
from typing import Optional

class TypefaceSource(str, Enum):
    SYSTEM = "system"
    FILE = "file"

@dataclass
class TypefaceLoadingInfo:
    typeface: skia.Typeface
    source: TypefaceSource
    filepath: Optional[str] # only valid on 'file' fonts
