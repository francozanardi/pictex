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
        .text_shadows(Shadow([1, 1], 1, 'black'), Shadow([2, 2], 2, 'black'))
        .box_shadows(Shadow([3, 3], 3, 'blue'), Shadow([4, 4], 4, 'blue'))
        .text_stroke(10, 'green')
        .underline(5.0, 'pink')
        .strikethrough(3.5, 'magenta')
        .padding(10, 20)
        .background_color('olive')
        .border_radius(15.5)
        .line_height(1.5)
        .text_align('right')
    )
    
    style = canvas._style
    assert style.font_family == "custom.ttf"
    assert style.font_fallbacks == ["fallback_1.ttf", "fallback_2"]
    assert style.font_size == 50
    assert style.font_weight == FontWeight.BOLD
    assert style.font_style == FontStyle.ITALIC
    assert style.color == SolidColor.from_str("#FF0000")
    assert style.text_shadows == [Shadow([1, 1], 1, SolidColor.from_str('black')), Shadow([2, 2], 2, SolidColor.from_str('black'))]
    assert style.box_shadows == [Shadow([3, 3], 3, SolidColor.from_str('blue')), Shadow([4, 4], 4, SolidColor.from_str('blue'))]
    assert style.text_stroke == OutlineStroke(10, SolidColor.from_str('green'))
    assert style.underline == TextDecoration(SolidColor.from_str('pink'), 5.0)
    assert style.strikethrough == TextDecoration(SolidColor.from_str('magenta'), 3.5)
    assert style.padding == Padding(10, 20, 10, 20)
    assert style.background_color == SolidColor.from_str('olive')
    assert style.border_radius == BorderRadius(BorderRadiusValue(15.5), BorderRadiusValue(15.5), BorderRadiusValue(15.5), BorderRadiusValue(15.5))
    assert style.line_height == 1.5
    assert style.text_align == TextAlign('right')

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
            .text_shadows(Shadow([0, 0], 0, color))
            .box_shadows(Shadow([0, 0], 0, color))
            .text_stroke(0, color)
            .underline(0, color)
            .strikethrough(0, color)
            .background_color(color)
        )
        style = canvas._style
        assert style.color == expected_color
        assert style.text_shadows == [Shadow([0, 0], 0, expected_color)]
        assert style.box_shadows == [Shadow([0, 0], 0, expected_color)]
        assert style.text_stroke == OutlineStroke(0, expected_color)
        assert style.underline == TextDecoration(expected_color, 0)
        assert style.strikethrough == TextDecoration(expected_color, 0)
        assert style.background_color == expected_color

def test_gradient_on_color_arguments():
    gradient = LinearGradient(['orange', 'red'], [0.3, 0.6], [0, 0], [1, 1])
    canvas = (
        Canvas()
        .color(gradient)
        .text_stroke(0, gradient)
        .underline(0, gradient)
        .strikethrough(0, gradient)
        .background_color(gradient)
    )
    style = canvas._style
    assert style.color == gradient
    assert style.text_stroke == OutlineStroke(0, gradient)
    assert style.underline == TextDecoration(gradient, 0)
    assert style.strikethrough == TextDecoration(gradient, 0)
    assert style.background_color == gradient

def test_padding():
    canvas = Canvas()
    canvas.padding(10)
    assert canvas._style.padding == Padding(10, 10, 10, 10)
    canvas.padding(10, 20)
    assert canvas._style.padding == Padding(10, 20, 10, 20)
    canvas.padding(1, 2, 3, 4)
    assert canvas._style.padding == Padding(1, 2, 3, 4)

def test_font_paths_can_be_object():
    canvas = Canvas()
    canvas.font_family(Path("myfont1.ttf"))
    canvas.font_fallbacks(Path("myfont2.ttf"), "myfont3.ttf", Path("myfont4.ttf"))

    style = canvas._style
    assert style.font_family == "myfont1.ttf"
    assert style.font_fallbacks == ["myfont2.ttf", "myfont3.ttf", "myfont4.ttf"]
