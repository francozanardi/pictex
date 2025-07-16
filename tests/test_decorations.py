from pictex import Canvas, LinearGradient
from .conftest import STATIC_FONT_PATH


def test_render_with_underline(file_regression, render_engine):
    """
    Tests a simple underline with default color (text color).
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(80)
        .color("#2980b9")
        .underline(thickness=4)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Underlined")
    check_func(file_regression, image)

def test_render_with_strikethrough_custom_color(file_regression, render_engine):
    """
    Tests a strikethrough with a specified custom color.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(80)
        .color("black")
        .strikethrough(thickness=5, color="#e74c3c")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Strikethrough")
    check_func(file_regression, image)

def test_render_with_multiple_decorations(file_regression, render_engine):
    """
    Verifies that multiple decorations can be applied to the same text.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(80)
        .color("black")
        .underline(thickness=3, color="#3498db")
        .strikethrough(thickness=3, color="#9b59b6")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Multi-Decorated")
    check_func(file_regression, image)

def test_render_with_gradient_decoration(file_regression, render_engine):
    """
    Confirms that a gradient can be applied to a text decoration line.
    """
    gradient = LinearGradient(colors=["#ff00ff", "#00ffff"])
    
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(80)
        .color("black")
        .underline(thickness=10, color=gradient)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Gradient Line")
    check_func(file_regression, image)
