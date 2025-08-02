from pictex import Canvas, LinearGradient, Row
from .conftest import VARIABLE_WGHT_FONT_PATH, IMAGE_PATH

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

def test_background_image_with_contain_mode(file_regression, render_engine):
    """
    Tests that the 'contain' size mode fits the entire image inside the
    container, potentially leaving empty space (letterboxing).
    """
    render_func, check_func = render_engine

    element = (
        Row()
        .size(400, 400)
        .background_image(IMAGE_PATH, size_mode='contain')
        .background_color("#333")
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_background_image_with_tile_mode(file_regression, render_engine):
    """
    Tests that the 'tile' size mode repeats the background image at its
    original size without scaling it.
    """
    render_func, check_func = render_engine

    element = (
        Row()
        .size(500, 500) # Larger than our test image
        .background_image(IMAGE_PATH, size_mode='tile')
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)
