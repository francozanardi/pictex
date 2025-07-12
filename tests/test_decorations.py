from pictex import Canvas, LinearGradient
from .utils import check_images_match, STATIC_FONT_PATH


def test_render_with_underline(file_regression):
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
    image = canvas.render("Underlined")
    check_images_match(file_regression, image)

def test_render_with_strikethrough_custom_color(file_regression):
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
    image = canvas.render("Strikethrough")
    check_images_match(file_regression, image)

def test_render_with_multiple_decorations(file_regression):
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
    image = canvas.render("Multi-Decorated")
    check_images_match(file_regression, image)

def test_render_with_gradient_decoration(file_regression):
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
    image = canvas.render("Gradient Line")
    check_images_match(file_regression, image)
