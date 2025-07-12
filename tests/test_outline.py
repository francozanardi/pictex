from pictex import Canvas, LinearGradient
from .utils import check_images_match, STATIC_FONT_PATH

def test_render_with_basic_outline(file_regression):
    """
    Tests a simple, solid-colored outline on a solid-colored text.
    This is the most common use case.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("yellow")
        .outline_stroke(width=8, color="black")
    )
    image = canvas.render("BASIC")
    check_images_match(file_regression, image)

def test_render_with_gradient_outline(file_regression):
    """
    Tests applying a linear gradient to the outline itself.
    This verifies that PaintSource works correctly for strokes.
    """
    outline_gradient = LinearGradient(colors=["#4A00E0", "#8E2DE2"])
    
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("white")
        .outline_stroke(width=10, color=outline_gradient)
    )
    image = canvas.render("GRADIENT")
    check_images_match(file_regression, image)

def test_outline_without_fill(file_regression):
    """
    Tests an edge case where the text color is fully transparent,
    resulting in a "hollow" text with only an outline.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("#00000000") 
        .outline_stroke(width=5, color="black")
    )
    image = canvas.render("HOLLOW")
    check_images_match(file_regression, image)
