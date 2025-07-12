# tests/test_background.py

from pictex import Canvas, LinearGradient
from .utils import check_images_match, VARIABLE_WGHT_FONT_PATH

def test_render_with_solid_background(file_regression):
    """
    Tests a basic background with a solid color, padding, and rounded corners.
    """
    canvas = (
        Canvas()
        .font_family(VARIABLE_WGHT_FONT_PATH)
        .font_size(80)
        .color("white")
        .padding(30, 60)
        .background_color("#34495e")
        .background_radius(20)
    )
    image = canvas.render("Solid Background")
    check_images_match(file_regression, image)

def test_render_with_gradient_background(file_regression):
    """
    Verifies that a gradient can be applied to the background.
    """
    gradient = LinearGradient(
        colors=["#1d2b64", "#f8cdda"],
        start_point=(0, 0),
        end_point=(1, 1)
    )
    
    canvas = (
        Canvas()
        .font_family(VARIABLE_WGHT_FONT_PATH)
        .font_size(80)
        .color("white")
        .padding(30, 60)
        .background_color(gradient)
        .background_radius(20)
    )
    image = canvas.render("Gradient BG")
    check_images_match(file_regression, image)

def test_background_without_padding(file_regression):
    """
    Tests an edge case where there is a background but no padding,
    the background should tightly wrap the text.
    """
    canvas = (
        Canvas()
        .font_family(VARIABLE_WGHT_FONT_PATH)
        .font_size(80)
        .color("white")
        .padding(0)
        .background_color("#c0392b")
    )
    image = canvas.render("No Padding")
    check_images_match(file_regression, image)
