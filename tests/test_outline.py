from pictex import Canvas, LinearGradient
from .conftest import STATIC_FONT_PATH

def test_render_with_basic_outline(file_regression, render_engine):
    """
    Tests a simple, solid-colored outline on a solid-colored text.
    This is the most common use case.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("yellow")
        .text_stroke(width=8, color="black")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "BASIC")
    check_func(file_regression, image)

def test_render_with_gradient_outline(file_regression, render_engine):
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
        .text_stroke(width=10, color=outline_gradient)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "GRADIENT")
    check_func(file_regression, image)

def test_outline_without_fill(file_regression, render_engine):
    """
    Tests an edge case where the text color is fully transparent,
    resulting in a "hollow" text with only an outline.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("#00000000")
        .text_stroke(width=5, color="black")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "HOLLOW")
    check_func(file_regression, image)

def test_stroke_mode_center(file_regression, render_engine):
    """
    Tests center stroke mode (CSS-compliant default).
    Stroke is centered on the text path (half inside, half outside).
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("blue")
        .text_stroke(width=8, color="orange", mode="center")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "CENTER")
    check_func(file_regression, image)

def test_stroke_mode_outline(file_regression, render_engine):
    """
    Tests outline stroke mode where the stroke is entirely outside the text.
    This prevents text from thinning at large stroke widths.
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("blue")
        .text_stroke(width=8, color="orange", mode="outline")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "OUTLINE")
    check_func(file_regression, image)

def test_stroke_mode_inline(file_regression, render_engine):
    """
    Tests inline stroke mode where the stroke is entirely inside the text.
    This makes the text appear thinner.
    
    NOTE: Known issue - inline mode does not render correctly in SVG (appears invisible).
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_size(120)
        .color("blue")
        .text_stroke(width=8, color="orange", mode="inline")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "INLINE")
    check_func(file_regression, image)

