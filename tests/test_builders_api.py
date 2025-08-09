from pictex import *
from pathlib import Path
from .conftest import IMAGE_PATH

def test_builders_fluent_api_and_style_building():
    """
    Verifies that the fluent API correctly builds the underlying Style object.
    """
    canvas = Canvas()
    row = Row()
    column = Column()
    image = Image(IMAGE_PATH)
    text = Text("test")
    with_position_builders = {row, column, image, text}
    container_builders = {row, column}
    all_builders = {row, column, image, text, canvas}

    for builder in all_builders:
        (
            builder.font_family("custom.ttf")
            .font_fallbacks("fallback_1.ttf", "fallback_2")
            .font_size(50)
            .font_weight(FontWeight.BOLD)
            .font_style(FontStyle.ITALIC)
            .line_height(1.5)
            .text_align('right')
            .color("#FF0000")
            .text_shadows(Shadow([1, 1], 1, 'black'), Shadow([2, 2], 2, 'black'))
            .text_stroke(10, 'green')
            .underline(5.0, 'pink')
            .strikethrough(3.5, 'magenta')
            .box_shadows(Shadow([3, 3], 3, 'blue'), Shadow([4, 4], 4, 'blue'))
            .padding(10, 20)
            .margin(30, 40)
            .background_color('olive')
            .background_image(IMAGE_PATH)
            .border(3, "red")
            .border_radius(15.5)
            .size(300, 300)
        )

        style = builder._style
        assert style.font_family == "custom.ttf"
        assert style.font_fallbacks == ["fallback_1.ttf", "fallback_2"]
        assert style.font_size == 50
        assert style.font_weight == FontWeight.BOLD
        assert style.font_style == FontStyle.ITALIC
        assert style.line_height == 1.5
        assert style.text_align == TextAlign('right')
        assert style.color == SolidColor.from_str("#FF0000")
        assert style.text_shadows == [Shadow([1, 1], 1, SolidColor.from_str('black')),
                                      Shadow([2, 2], 2, SolidColor.from_str('black'))]
        assert style.text_stroke == OutlineStroke(10, SolidColor.from_str('green'))
        assert style.underline == TextDecoration(SolidColor.from_str('pink'), 5.0)
        assert style.strikethrough == TextDecoration(SolidColor.from_str('magenta'), 3.5)

        assert style.box_shadows == [Shadow([3, 3], 3, SolidColor.from_str('blue')),
                                     Shadow([4, 4], 4, SolidColor.from_str('blue'))]
        assert style.padding == Padding(10, 20, 10, 20)
        assert style.margin == Margin(30, 40, 30, 40)
        assert style.background_color == SolidColor.from_str('olive')
        assert style.background_image == BackgroundImage(IMAGE_PATH)
        assert style.border == Border(3, SolidColor.from_str('red'))
        assert style.border_radius == BorderRadius(BorderRadiusValue(15.5), BorderRadiusValue(15.5),
                                                   BorderRadiusValue(15.5), BorderRadiusValue(15.5))
        assert style.width == SizeValue(SizeValueMode.ABSOLUTE, 300)
        assert style.height == SizeValue(SizeValueMode.ABSOLUTE, 300)

    for builder in with_position_builders:
        builder.absolute_position("center", "70%")

        style = builder._style
        assert style.position == Position(container_anchor_x=0.5, content_anchor_x=0.5, container_anchor_y=0.7, mode = PositionMode.ABSOLUTE)

        builder.position("center", "70%")
        assert style.position == Position(container_anchor_x=0.5, content_anchor_x=0.5, container_anchor_y=0.7, mode = PositionMode.RELATIVE)

    for builder in container_builders:
        builder.gap(10)

        style = builder._style
        assert style.gap == 10

    row.horizontal_distribution("center")
    row.vertical_align("bottom")
    style = row._style
    assert style.horizontal_distribution == HorizontalDistribution("center")
    assert style.vertical_alignment == VerticalAlignment("bottom")

    column.vertical_distribution("bottom")
    column.horizontal_align("center")
    style = column._style
    assert style.vertical_distribution == VerticalDistribution("bottom")
    assert style.horizontal_alignment == HorizontalAlignment("center")

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

def test_margin():
    text = Text("")
    text.margin(10)
    assert text._style.margin == Margin(10, 10, 10, 10)
    text.margin(10, 20)
    assert text._style.margin == Margin(10, 20, 10, 20)
    text.margin(1, 2, 3, 4)
    assert text._style.margin == Margin(1, 2, 3, 4)

def test_border_radius():
    canvas = Canvas()
    canvas.border_radius(10)
    assert canvas._style.border_radius == BorderRadius(BorderRadiusValue(10), BorderRadiusValue(10), BorderRadiusValue(10), BorderRadiusValue(10))
    canvas.border_radius(10, "20%")
    assert canvas._style.border_radius == BorderRadius(BorderRadiusValue(10), BorderRadiusValue(20, 'percent'), BorderRadiusValue(10), BorderRadiusValue(20, 'percent'))
    canvas.border_radius(1, "2%", 3, "4%")
    assert canvas._style.border_radius == BorderRadius(BorderRadiusValue(1), BorderRadiusValue(2, 'percent'), BorderRadiusValue(3), BorderRadiusValue(4, 'percent'))

def test_size():
    canvas = Canvas()
    canvas.size()
    assert canvas._style.width == None
    assert canvas._style.height == None
    canvas.size(width=300)
    assert canvas._style.width == SizeValue(SizeValueMode.ABSOLUTE, 300)
    assert canvas._style.height == None
    canvas.size(height=300)
    assert canvas._style.width == SizeValue(SizeValueMode.ABSOLUTE, 300)
    assert canvas._style.height == SizeValue(SizeValueMode.ABSOLUTE, 300)
    canvas.size("10%", "20%")
    assert canvas._style.width == SizeValue(SizeValueMode.PERCENT, 10)
    assert canvas._style.height == SizeValue(SizeValueMode.PERCENT, 20)
    canvas.size("fit-background-image", "fit-content")
    assert canvas._style.width == SizeValue(SizeValueMode.FIT_BACKGROUND_IMAGE)
    assert canvas._style.height == SizeValue(SizeValueMode.FIT_CONTENT)
    canvas.fit_background_image()
    assert canvas._style.width == SizeValue(SizeValueMode.FIT_BACKGROUND_IMAGE)
    assert canvas._style.height == SizeValue(SizeValueMode.FIT_BACKGROUND_IMAGE)

def test_position():
    builder = Text("")
    builder.position(10, 20)
    assert builder._style.position == Position(x_offset=10, y_offset=20, mode=PositionMode.RELATIVE)
    builder.absolute_position("30%", "40%")
    assert builder._style.position == Position(container_anchor_x=0.3, container_anchor_y=0.4, mode=PositionMode.ABSOLUTE)
    builder.position("left", "bottom")
    assert builder._style.position == Position(container_anchor_y=1.0, content_anchor_y=1.0, mode=PositionMode.RELATIVE)

def test_font_paths_can_be_object():
    canvas = Canvas()
    canvas.font_family(Path("myfont1.ttf"))
    canvas.font_fallbacks(Path("myfont2.ttf"), "myfont3.ttf", Path("myfont4.ttf"))

    style = canvas._style
    assert style.font_family == "myfont1.ttf"
    assert style.font_fallbacks == ["myfont2.ttf", "myfont3.ttf", "myfont4.ttf"]
