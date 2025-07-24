from dataclasses import dataclass, field, fields
from typing import Optional, Any
from .effects import Shadow, OutlineStroke
from .position import Position
from .typography import TextAlign, FontWeight, FontStyle
from .paint_source import PaintSource
from .decoration import TextDecoration
from .color import SolidColor

@dataclass
class Style:
    """
    A comprehensive container for all text styling properties.
    This is the core data model for the library.
    """
    # Properties that can be inherited.
    font_family: Optional[str] = None
    font_fallbacks: list[str] = field(default_factory=list)
    font_size: float = 50
    font_weight: FontWeight = FontWeight.NORMAL
    font_style: FontStyle = FontStyle.NORMAL
    line_height: float = 1.0  # Multiplier for the font size, like in CSS
    text_align: TextAlign = TextAlign.LEFT
    color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0))
    text_shadows: list[Shadow] = field(default_factory=list)
    underline: TextDecoration = None
    strikethrough: TextDecoration = None

    # Properties that cannot be inherited.
    box_shadows: list[Shadow] = field(default_factory=list)
    outline_stroke: Optional[OutlineStroke] = None
    padding: tuple[float, float, float, float] = (0, 0, 0, 0) # Top, Right, Bottom, Left. TODO: create padding class
    background_color: PaintSource = field(default_factory=lambda: SolidColor(0, 0, 0, 0))
    box_radius: float = 0.0
    position: Optional[Position] = None

    # FIXME: this is not being copied correctly
    #  and, it's not taking into account when a list is modified, for example, adding a value.
    _touched_fields: set[str] = field(default_factory=set, init=False, repr=False)

    def __setattr__(self, key: str, value: Any):
        if "_touched_fields" in self.__dict__ and key in self.get_field_names():
            self._touched_fields.add(key)
        super().__setattr__(key, value)

    def is_explicit(self, field_name: str) -> bool:
        return field_name in self._touched_fields

    def is_inheritable(self, field_name: str) -> bool:
        not_inheritable_props = [
            "box_shadows",
            "outline_stroke",
            "padding",
            "background_color",
            "box_radius",
            "position"
        ]
        if field_name not in self.get_field_names():
            raise ValueError(f"Field '{field_name}' doesn't exist.")

        return field_name not in not_inheritable_props

    def get_field_names(self) -> list[str]:
        return [f.name for f in fields(self)]
