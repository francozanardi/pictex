from pictex import *
from .conftest import VARIABLE_WGHT_FONT_PATH, IMAGE_PATH

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
        .line_height(1.3)
        .text_align(TextAlign.CENTER)
        .padding(30, 40)
        .margin(25)
        .background_color(LinearGradient(colors=["#414345", "#232526"]))
        .border(5, LinearGradient(["blue", "cyan"]))
        .border_radius(25)
        .text_shadows(Shadow(offset=(3, 3), blur_radius=5, color="#FFFFFF50"))
        .box_shadows(Shadow(offset=(10, 10), blur_radius=20, color="#000000A0"))
        .underline(thickness=4, color="#FFD700")
        .strikethrough(thickness=4)
    )

    text_1 = Text("Kitchen Sink").color(LinearGradient(colors=["#00F260", "#0575E6"])).font_weight(FontWeight.BOLD)
    text_2 = Text("Test!").color("yellow").text_stroke(width=3, color="black").font_style(FontStyle.ITALIC)
    image = Image(IMAGE_PATH).resize(0.5)
    col = (
        Column(text_1, text_2, image)
        .vertical_distribution('space-around')
        .horizontal_align('center').gap(20)
        .border(5, "blue")
        .background_color("cyan")
    )

    render_func, check_func = render_engine
    image = render_func(canvas, col)
    check_func(file_regression, image)
