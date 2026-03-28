from pictex import *


def test_line_height_auto_default(file_regression, render_engine):
    """
    Tests that the default line height (auto) uses font metrics to determine
    the vertical space between lines. No explicit line_height call is made.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(100)
        .background_color("pink")
        .border(10, "red")
    )
    render_func, check_func = render_engine
    image = render_func(canvas, Text("pgÝÁ\nÝÁpg"))
    check_func(file_regression, image)


def test_line_height_explicit_multiplier(file_regression, render_engine):
    """
    Tests that an explicit line_height multiplier overrides the auto (font metrics)
    default and controls vertical spacing as a multiple of font_size.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(100)
        .background_color("pink")
        .border(10, "red")
        .line_height(1.5)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, Text("pgÝÁ\nÝÁpg"))
    check_func(file_regression, image)
