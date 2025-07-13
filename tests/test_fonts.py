from pictex import *
from .utils import check_images_match, STATIC_FONT_PATH, VARIABLE_WGHT_FONT_PATH, JAPANESE_FONT_PATH
import pytest

def test_render_with_custom_static_font(file_regression):
    """Tests loading a static font from a .ttf file."""
    canvas = Canvas().font_family(str(STATIC_FONT_PATH)).font_size(70)
    image = canvas.render("Custom Static Font")
    check_images_match(file_regression, image)

@pytest.mark.parametrize("weight, expected_style", [
    (FontWeight.LIGHT, "Light"),
    (FontWeight.NORMAL, "Regular"),
    (FontWeight.BOLD, "Bold"),
    (900, "Black"),
])
def test_render_with_variable_font_weight(file_regression, weight, expected_style):
    """Tests a variable font by rendering it at different weights."""
    canvas = (
        Canvas()
        .font_family(str(VARIABLE_WGHT_FONT_PATH))
        .font_size(70)
        .font_weight(weight)
        .color("black")
    )
    image = canvas.render(f"Weight: {expected_style}")
    check_images_match(file_regression, image)

def test_render_with_font_fallback_for_emoji(file_regression):
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
    image = canvas.render("Fox 🦊")
    check_images_match(file_regression, image)

def test_render_with_system_font_fallback(file_regression):
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
    image = canvas.render("PF | 世界 | Again, PF | ✨ | PF.")
    check_images_match(file_regression, image)

@pytest.mark.parametrize("text, align", [
    ("Basic Text", "left"),
    ("Centered\nMulti-line", "center"),
    ("Right Aligned\nLonger First Line", "right")
])
def test_render_basic_text_and_alignment(file_regression, text, align):
    """Tests basic rendering and alignment."""
    canvas = Canvas().font_family("Arial").alignment(align)
    image = canvas.render(text)
    check_images_match(file_regression, image)

def test_render_with_default_font(file_regression):
    """
    Tests default system font is used when font is not set
    """
    canvas = (
        Canvas()
        .font_size(70)
        .color("orange")
    )
    image = canvas.render("Default font")
    check_images_match(file_regression, image)

def test_render_with_invalid_fonts(file_regression):
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
    image = canvas.render("Invalid is ignored")
    check_images_match(file_regression, image)
