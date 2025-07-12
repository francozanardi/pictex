from pictex import Canvas, LinearGradient
from .utils import check_images_match

def test_gradient_on_text_fill(file_regression):
    """
    A basic test to confirm a gradient can be applied to the text fill.
    This is the primary use case.
    """
    gradient = LinearGradient(
        colors=["#f12711", "#f5af19"],
        start_point=(0, 0.5), # Horizontal
        end_point=(1, 0.5)
    )
    
    canvas = (
        Canvas()
        .font_size(120)
        .color(gradient)
    )
    image = canvas.render("GRADIENT")
    check_images_match(file_regression, image)
    
def test_gradient_direction_vertical(file_regression):
    """
    Tests that start_point and end_point correctly create a vertical gradient.
    """
    gradient = LinearGradient(
        colors=["#00f6ff", "#0052ff"],
        start_point=(0.5, 0), # Top-center
        end_point=(0.5, 1)   # Bottom-center
    )
    
    canvas = (
        Canvas()
        .font_size(120)
        .color(gradient)
    )
    image = canvas.render("VERTICAL")
    check_images_match(file_regression, image)

def test_gradient_with_custom_stops(file_regression):
    """
    Verifies that the `stops` parameter works, allowing for non-uniform
    color distribution in the gradient.
    """
    gradient = LinearGradient(
        colors=["#e96443", "#904e95"],
        stops=[0.2, 0.8]
    )
    
    canvas = (
        Canvas()
        .font_size(120)
        .padding(20)
        .background_color("#222222")
        .color(gradient)
    )
    image = canvas.render("STOPS")
    check_images_match(file_regression, image)
