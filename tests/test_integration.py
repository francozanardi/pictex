from pictex import *
from .conftest import VARIABLE_WGHT_FONT_PATH

def test_kitchen_sink_all_features_combined(file_regression, render_engine):
    """
    This is a visual integration test that combines a large number of features
    to ensure they work together without unexpected visual artifacts.
    
    It validates the result of the fluent API smoke test.
    """

    canvas = (
        Canvas()
        .font_family(str(VARIABLE_WGHT_FONT_PATH))
        .font_size(80)
        .font_weight(FontWeight.BLACK)
        .font_style(FontStyle.ITALIC)
        .font_smoothing(FontSmoothing.STANDARD)
        .line_height(1.3)
        .text_align(Alignment.CENTER)
        .padding(30, 40)
        .background_color(LinearGradient(colors=["#414345", "#232526"]))
        .background_radius(25)
        .color(LinearGradient(colors=["#00F260", "#0575E6"]))
        .add_shadow(offset=(3, 3), blur_radius=5, color="#FFFFFF50")
        .add_box_shadow(offset=(10, 10), blur_radius=20, color="#000000A0")
        .outline_stroke(width=3, color="black")
        .underline(thickness=4, color="#FFD700")
    )
    
    render_func, check_func = render_engine
    image = render_func(canvas, "Kitchen Sink\nTest!")
    check_func(file_regression, image)
