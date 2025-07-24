from pictex import *
from pathlib import Path

def test_canvas_fluent_api_and_style_building():
    """
    Verifies that the fluent API correctly builds the underlying Style object.
    """

    canvas = (
        Canvas()
        .font_family("custom.ttf")
        .font_fallbacks("fallback_1.ttf", "fallback_2")
        .font_size(50)
        .font_weight(FontWeight.BOLD)
        .font_style(FontStyle.ITALIC)
        .color("#FF0000")
        .add_shadow([1, 1], 1, 'black')
        .add_shadow([2, 2], 2, 'black')
        .add_box_shadow([3, 3], 3, 'blue')
        .add_box_shadow([4, 4], 4, 'blue')
        .outline_stroke(10, 'green')
        .underline(5.0, 'pink')
        .strikethrough(3.5, 'magenta')
        .padding(10, 20)
        .background_color('olive')
        .background_radius(15.5)
        .line_height(1.5)
        .text_align('right')
        .font_smoothing(FontSmoothing.STANDARD)
    )
    
    style = canvas._style
    assert style.font.family == "custom.ttf"
    assert style.font_fallbacks == ["fallback_1.ttf", "fallback_2"]
    assert style.font.size == 50
    assert style.font.weight == FontWeight.BOLD
    assert style.font.style == FontStyle.ITALIC
    assert style.color == SolidColor.from_str("#FF0000")
    assert style.text_shadows == [Shadow([1, 1], 1, SolidColor.from_str('black')), Shadow([2, 2], 2, SolidColor.from_str('black'))]
    assert style.box_shadows == [Shadow([3, 3], 3, SolidColor.from_str('blue')), Shadow([4, 4], 4, SolidColor.from_str('blue'))]
    assert style.outline_stroke == OutlineStroke(10, SolidColor.from_str('green'))
    assert style.decorations == [
        TextDecoration(DecorationLine.UNDERLINE, SolidColor.from_str('pink'), 5.0),
        TextDecoration(DecorationLine.STRIKETHROUGH, SolidColor.from_str('magenta'), 3.5)
    ]
    assert style.padding == (10, 20, 10, 20)
    assert style.background.color == SolidColor.from_str('olive')
    assert style.background.corner_radius == 15.5
    assert style.font.line_height == 1.5
    assert style.text_align == Alignment('right')
    assert style.font.smoothing == FontSmoothing.STANDARD

def test_color_formats():
    color_formats = [
        'red',
        '#F00',
        '#FF0000',
        '#FF0000FF',
        SolidColor(255, 0, 0),
        SolidColor(255, 0, 0, 255),
    ]
    expected_color = SolidColor(255, 0, 0, 255)
    for color in color_formats:
        canvas = (
            Canvas()
            .color(color)
            .add_shadow([0, 0], 0, color)
            .add_box_shadow([0, 0], 0, color)
            .outline_stroke(0, color)
            .underline(0, color)
            .strikethrough(0, color)
            .background_color(color)
        )
        style = canvas._style
        assert style.color == expected_color
        assert style.text_shadows == [Shadow([0, 0], 0, expected_color)]
        assert style.box_shadows == [Shadow([0, 0], 0, expected_color)]
        assert style.outline_stroke == OutlineStroke(0, expected_color)
        assert style.decorations == [
            TextDecoration(DecorationLine.UNDERLINE, expected_color, 0),
            TextDecoration(DecorationLine.STRIKETHROUGH, expected_color, 0),
        ]
        assert style.background.color == expected_color

def test_gradient_on_color_arguments():
    gradient = LinearGradient(['orange', 'red'], [0.3, 0.6], [0, 0], [1, 1])
    canvas = (
        Canvas()
        .color(gradient)
        .outline_stroke(0, gradient)
        .underline(0, gradient)
        .strikethrough(0, gradient)
        .background_color(gradient)
    )
    style = canvas._style
    assert style.color == gradient
    assert style.outline_stroke == OutlineStroke(0, gradient)
    assert style.decorations == [
        TextDecoration(DecorationLine.UNDERLINE, gradient, 0),
        TextDecoration(DecorationLine.STRIKETHROUGH, gradient, 0),
    ]
    assert style.background.color == gradient

def test_padding():
    canvas = Canvas()
    canvas.padding(10)
    assert canvas._style.padding == (10, 10, 10, 10)
    canvas.padding(10, 20)
    assert canvas._style.padding == (10, 20, 10, 20)
    canvas.padding(1, 2, 3, 4)
    assert canvas._style.padding == (1, 2, 3, 4)

def test_font_paths_can_be_object():
    canvas = Canvas()
    canvas.font_family(Path("myfont1.ttf"))
    canvas.font_fallbacks(Path("myfont2.ttf"), "myfont3.ttf", Path("myfont4.ttf"))

    style = canvas._style
    assert style.font.family == "myfont1.ttf"
    assert style.font_fallbacks == ["myfont2.ttf", "myfont3.ttf", "myfont4.ttf"]
