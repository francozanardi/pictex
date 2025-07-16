from pictex import Canvas, LinearGradient

def test_gradient_on_text_fill(file_regression, render_engine):
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
        .font_family("Arial")
        .font_size(120)
        .color(gradient)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "GRADIENT")
    check_func(file_regression, image)
    
def test_gradient_direction_vertical(file_regression, render_engine):
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
        .font_family("Arial")
        .font_size(120)
        .color(gradient)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "VERTICAL")
    check_func(file_regression, image)

def test_gradient_with_custom_stops(file_regression, render_engine):
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
        .font_family("Arial")
        .font_size(120)
        .padding(20)
        .background_color("#222222")
        .color(gradient)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "STOPS")
    check_func(file_regression, image)
