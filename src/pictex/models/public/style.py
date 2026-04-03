from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import Optional
from .border import Border, BorderRadius
from .background import BackgroundImage
from .effects import Shadow, OutlineStroke
from .layout import Margin, Padding, JustifyContent, AlignItems, AlignSelf, FlexWrap, TextBoxEdge
from .position import Position
from .transform import Transform
from .style_property import StyleProperty
from .typography import TextAlign, FontWeight, FontStyle, TextWrap
from .text_direction import TextDirection
from .paint_source import PaintSource
from .decoration import TextDecoration
from .color import SolidColor
from .size import SizeValue
from .line_height import LineHeight
from .letter_spacing import LetterSpacing
from .overflow import Overflow


@dataclass
class Style:
    """
    A comprehensive container for all text styling properties.
    This is the core data model for the library.
    """
    # Properties that can be inherited.
    font_family: StyleProperty[Optional[str]] = field(default_factory=lambda: StyleProperty(None))
    font_fallbacks: StyleProperty[list[str]] = field(default_factory=lambda: StyleProperty([]))
    font_size: StyleProperty[float] = field(default_factory=lambda: StyleProperty(50))
    font_weight: StyleProperty[FontWeight] = field(default_factory=lambda: StyleProperty(FontWeight.NORMAL))
    font_style: StyleProperty[FontStyle] = field(default_factory=lambda: StyleProperty(FontStyle.NORMAL))
    line_height: StyleProperty[LineHeight] = field(default_factory=lambda: StyleProperty(LineHeight.auto()))
    text_align: StyleProperty[Optional[TextAlign]] = field(default_factory=lambda: StyleProperty(None))
    color: StyleProperty[PaintSource] = field(default_factory=lambda: StyleProperty(SolidColor(0, 0, 0)))
    text_shadows: StyleProperty[list[Shadow]] = field(default_factory=lambda: StyleProperty([]))
    text_stroke: StyleProperty[Optional[OutlineStroke]] = field(default_factory=lambda: StyleProperty(None))
    underline: StyleProperty[Optional[TextDecoration]] = field(default_factory=lambda: StyleProperty(None))
    strikethrough: StyleProperty[Optional[TextDecoration]] = field(default_factory=lambda: StyleProperty(None))
    text_wrap: StyleProperty[TextWrap] = field(default_factory=lambda: StyleProperty(TextWrap.NORMAL))
    direction: StyleProperty[Optional[TextDirection]] = field(default_factory=lambda: StyleProperty(None))
    text_box_edge: StyleProperty[TextBoxEdge] = field(default_factory=lambda: StyleProperty(TextBoxEdge()))
    letter_spacing: StyleProperty[LetterSpacing] = field(default_factory=lambda: StyleProperty(LetterSpacing.normal()))

    # Properties that cannot be inherited.
    box_shadows: StyleProperty[list[Shadow]] = field(default_factory=lambda: StyleProperty([], inheritable=False))
    padding: StyleProperty[Padding] = field(default_factory=lambda: StyleProperty(Padding(), inheritable=False))
    margin: StyleProperty[Margin] = field(default_factory=lambda: StyleProperty(Margin(), inheritable=False))
    background_color: StyleProperty[Optional[PaintSource]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    background_image: StyleProperty[Optional[BackgroundImage]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    border: StyleProperty[Optional[Border]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    border_radius: StyleProperty[Optional[BorderRadius]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    position: StyleProperty[Optional[Position]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    transform: StyleProperty[Optional[Transform]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    width: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    height: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    min_width: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    max_width: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    min_height: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    max_height: StyleProperty[Optional[SizeValue]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    aspect_ratio: StyleProperty[Optional[float]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    justify_content: StyleProperty[JustifyContent] = field(
        default_factory=lambda: StyleProperty(JustifyContent.START, inheritable=False)
    )
    align_items: StyleProperty[AlignItems] = field(
        default_factory=lambda: StyleProperty(AlignItems.START, inheritable=False)
    )
    align_self: StyleProperty[AlignSelf] = field(
        default_factory=lambda: StyleProperty(AlignSelf.AUTO, inheritable=False)
    )
    flex_grow: StyleProperty[float] = field(
        default_factory=lambda: StyleProperty(0.0, inheritable=False)
    )
    flex_shrink: StyleProperty[float] = field(
        default_factory=lambda: StyleProperty(1.0, inheritable=False)
    )
    flex_wrap: StyleProperty[FlexWrap] = field(
        default_factory=lambda: StyleProperty(FlexWrap.NOWRAP, inheritable=False)
    )
    gap: StyleProperty[float] = field(default_factory=lambda: StyleProperty(0.0, inheritable=False))
    overflow: StyleProperty[Overflow] = field(default_factory=lambda: StyleProperty(Overflow.VISIBLE, inheritable=False))

    def is_explicit(self, field_name: str) -> bool:
        property: Optional[StyleProperty] = getattr(self, field_name)
        if not property:
            raise ValueError(f"Field '{field_name}' doesn't exist.")
        return property.was_set

    def is_inheritable(self, field_name: str) -> bool:
        property: Optional[StyleProperty] = getattr(self, field_name)
        if not property:
            raise ValueError(f"Field '{field_name}' doesn't exist.")
        return property.is_inheritable

    def get_field_names(self) -> list[str]:
        return [f.name for f in fields(self)]

    def inherit_from(self, parent: "Style", only_explicit: bool = False) -> None:
        """Inherit inheritable non-explicit fields from parent in-place.

        Args:
            parent: The parent style to inherit from.
            only_explicit: When True, only copy fields that were explicitly set
                on the parent (used when parent is a raw/partial style rather
                than a fully computed one).
        """
        for field_name in self.get_field_names():
            if not self.is_inheritable(field_name):
                continue
            if self.is_explicit(field_name):
                continue
            if only_explicit and not parent.is_explicit(field_name):
                continue
            setattr(self, field_name, deepcopy(getattr(parent, field_name)))
