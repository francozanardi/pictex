from dataclasses import dataclass, field, fields
from typing import Optional
from .border import Border, BorderRadius
from .background import BackgroundImage
from .effects import Shadow, OutlineStroke
from .layout import Margin, Padding, HorizontalDistribution, VerticalAlignment, HorizontalAlignment, VerticalDistribution
from .position import Position
from .style_property import StyleProperty
from .typography import TextAlign, FontWeight, FontStyle
from .paint_source import PaintSource
from .decoration import TextDecoration
from .color import SolidColor
from .size import Size


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
    line_height: StyleProperty[float] = field(default_factory=lambda: StyleProperty(1.0))  # Multiplier for the font size, like in CSS
    text_align: StyleProperty[TextAlign] = field(default_factory=lambda: StyleProperty(TextAlign.LEFT))
    color: StyleProperty[PaintSource] = field(default_factory=lambda: StyleProperty(SolidColor(0, 0, 0)))
    text_shadows: StyleProperty[list[Shadow]] = field(default_factory=lambda: StyleProperty([]))
    text_stroke: StyleProperty[Optional[OutlineStroke]] = field(default_factory=lambda: StyleProperty(None))
    underline: StyleProperty[Optional[TextDecoration]] = field(default_factory=lambda: StyleProperty(None))
    strikethrough: StyleProperty[Optional[TextDecoration]] = field(default_factory=lambda: StyleProperty(None))

    # Properties that cannot be inherited.
    box_shadows: StyleProperty[list[Shadow]] = field(default_factory=lambda: StyleProperty([], inheritable=False))
    padding: StyleProperty[Padding] = field(default_factory=lambda: StyleProperty(Padding(), inheritable=False))
    margin: StyleProperty[Margin] = field(default_factory=lambda: StyleProperty(Margin(), inheritable=False))
    background_color: StyleProperty[Optional[PaintSource]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    background_image: StyleProperty[Optional[BackgroundImage]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    border: StyleProperty[Optional[Border]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    border_radius: StyleProperty[Optional[BorderRadius]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    position: StyleProperty[Optional[Position]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    size: StyleProperty[Optional[Size]] = field(default_factory=lambda: StyleProperty(None, inheritable=False))
    horizontal_distribution: StyleProperty[HorizontalDistribution] = field(
        default_factory=lambda: StyleProperty(HorizontalDistribution.LEFT, inheritable=False)
    )
    vertical_alignment: StyleProperty[VerticalAlignment] = field(
        default_factory=lambda: StyleProperty(VerticalAlignment.TOP, inheritable=False)
    )
    vertical_distribution: StyleProperty[VerticalDistribution] = field(
        default_factory=lambda: StyleProperty(VerticalDistribution.TOP, inheritable=False)
    )
    horizontal_alignment: StyleProperty[HorizontalAlignment] = field(
        default_factory=lambda: StyleProperty(HorizontalAlignment.LEFT, inheritable=False)
    )
    gap: StyleProperty[float] = field(default_factory=lambda: StyleProperty(0.0, inheritable=False))

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
