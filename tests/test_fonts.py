from pictex import *
from .conftest import STATIC_FONT_PATH, VARIABLE_WGHT_FONT_PATH, JAPANESE_FONT_PATH
import pytest

def test_render_with_custom_static_font(file_regression, render_engine):
    """Tests loading a static font from a .ttf file."""
    canvas = Canvas().font_family(str(STATIC_FONT_PATH)).font_size(70)
    render_func, check_func = render_engine
    image = render_func(canvas, "Custom Static Font")
    check_func(file_regression, image)

@pytest.mark.parametrize("weight, expected_style", [
    (FontWeight.LIGHT, "Light"),
    (FontWeight.NORMAL, "Regular"),
    (FontWeight.BOLD, "Bold"),
    (900, "Black"),
])
def test_render_with_variable_font_weight(file_regression, render_engine, weight, expected_style):
    """Tests a variable font by rendering it at different weights."""
    canvas = (
        Canvas()
        .font_family(str(VARIABLE_WGHT_FONT_PATH))
        .font_size(70)
        .font_weight(weight)
        .color("black")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, f"Weight: {expected_style}")
    check_func(file_regression, image)

def test_render_with_font_fallback_for_emoji(file_regression, render_engine):
    """
    Tests that font fallback works correctly by rendering an emoji
    that does not exist in the primary font.
    """
    canvas = (
        Canvas()
        .font_family(str(STATIC_FONT_PATH)) # No emojies support
        .font_size(70)
        .color("black")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Fox 🦊")
    check_func(file_regression, image)

def test_render_with_system_font_fallback(file_regression, render_engine):
    """
    Tests that a system font can be used as a fallback.
    """
    canvas = (
        Canvas()
        .font_family(str(STATIC_FONT_PATH)) # No emojies and japanese support
        .font_fallbacks(str(JAPANESE_FONT_PATH))
        .font_size(70)
        .color("black")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "PF | 世界 | Again, PF | ✨ | PF.")
    check_func(file_regression, image)

@pytest.mark.parametrize("text, align", [
    ("Basic Text", "left"),
    ("Centered\nMulti-line", "center"),
    ("Right Aligned\nLonger First Line", "right")
])
def test_render_basic_text_and_alignment(file_regression, render_engine, text, align):
    """Tests basic rendering and alignment."""
    canvas = Canvas().font_family("Arial").text_align(align)
    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_render_with_default_font(file_regression, render_engine):
    """
    Tests default system font is used when font is not set
    """
    canvas = (
        Canvas()
        .font_size(70)
        .color("orange")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Default font")
    check_func(file_regression, image)

def test_render_with_invalid_fonts(file_regression, render_engine):
    """
    Tests invalid fonts are ignored
    """
    canvas = (
        Canvas()
        .font_family("invalid")
        .font_fallbacks("invalid", STATIC_FONT_PATH, "invalid")
        .font_size(70)
        .color("cyan")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Invalid is ignored")
    check_func(file_regression, image)
