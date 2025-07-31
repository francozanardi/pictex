from pictex import Canvas, LinearGradient
from .conftest import VARIABLE_WGHT_FONT_PATH

def test_render_with_solid_background(file_regression, render_engine):
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
        .border_radius(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Solid Background")
    check_func(file_regression, image)

def test_render_with_gradient_background(file_regression, render_engine):
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
        .border_radius(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Gradient BG")
    check_func(file_regression, image)

def test_background_without_padding(file_regression, render_engine):
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
    render_func, check_func = render_engine
    image = render_func(canvas, "No Padding")
    check_func(file_regression, image)
