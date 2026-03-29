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
            .text_stroke(10, 'green', mode='outline')
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
        assert style.line_height == LineHeight.multiplier(1.5)
        assert style.text_align == TextAlign('right')
        assert style.color == SolidColor.from_str("#FF0000")
        assert style.text_shadows == [Shadow([1, 1], 1, SolidColor.from_str('black')),
                                      Shadow([2, 2], 2, SolidColor.from_str('black'))]
        assert style.text_stroke == OutlineStroke(10, SolidColor.from_str('green'), StrokeMode.OUTLINE)
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
        builder.place("center", "70%")

        style = builder._style
        position = style.position.get()
        assert position.type == PositionType.FIXED  # place() uses canvas-relative positioning
        assert position.inset.top == "70%"
        assert position.inset.left == "50%"
        transform = style.transform.get()
        assert transform.translate_x == "-50%"
        assert transform.translate_y == "-70.0%"

    for builder in container_builders:
        builder.gap(10)

        style = builder._style
        assert style.gap == 10

    row.justify_content("center")
    row.align_items("start")
    style = row._style
    assert style.justify_content == JustifyContent("center")
    assert style.align_items == AlignItems("start")

    column.justify_content("start")
    column.align_items("center")
    style = column._style
    assert style.justify_content == JustifyContent("start")
    assert style.align_items == AlignItems("center")

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
        assert style.text_stroke == OutlineStroke(0, expected_color, StrokeMode.CENTER)
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
    assert style.text_stroke == OutlineStroke(0, gradient, StrokeMode.CENTER)
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

def test_width_and_height_sugar():
    canvas = Canvas()
    canvas.width(500)
    assert canvas._style.width == SizeValue(SizeValueMode.ABSOLUTE, 500)
    assert canvas._style.height == None
    
    canvas.height("50%")
    assert canvas._style.width == SizeValue(SizeValueMode.ABSOLUTE, 500)
    assert canvas._style.height == SizeValue(SizeValueMode.PERCENT, 50)
    
    canvas.width("fit-content")
    assert canvas._style.width == SizeValue(SizeValueMode.FIT_CONTENT)

def test_position():
    builder = Text("")
    
    # Test relative_position with pixel offsets
    builder.relative_position(top=10, left=20)
    position = builder._style.position.get()
    assert position.type == PositionType.RELATIVE
    assert position.inset.top == 10
    assert position.inset.left == 20
    
    # Test absolute_position with percentages
    builder.absolute_position(top="30%", left="40%")
    position = builder._style.position.get()
    assert position.type == PositionType.ABSOLUTE
    assert position.inset.top == "30%"
    assert position.inset.left == "40%"
    
    # Test place() for anchor-based positioning
    builder.place("left", "bottom")
    position = builder._style.position.get()
    assert position.type == PositionType.FIXED  # place() uses canvas-relative positioning
    assert position.inset.top is None
    assert position.inset.left == 0
    assert position.inset.bottom == 0

def test_font_paths_can_be_object():
    canvas = Canvas()
    canvas.font_family(Path("myfont1.ttf"))
    canvas.font_fallbacks(Path("myfont2.ttf"), "myfont3.ttf", Path("myfont4.ttf"))

    style = canvas._style
    assert style.font_family == "myfont1.ttf"
    assert style.font_fallbacks == ["myfont2.ttf", "myfont3.ttf", "myfont4.ttf"]

def test_font_weight():
    text = Text("test")
    
    # Enum
    text.font_weight(FontWeight.BOLD)
    assert text._style.font_weight == FontWeight.BOLD
    
    # Integer
    text.font_weight(400)
    assert text._style.font_weight == FontWeight.NORMAL
    
    # String - exact name
    text.font_weight("BLACK")
    assert text._style.font_weight == FontWeight.BLACK
    
    # String - lowercase name
    text.font_weight("bold")
    assert text._style.font_weight == FontWeight.BOLD
    
    # String - CSS style name
    text.font_weight("extra-bold")
    assert text._style.font_weight == FontWeight.EXTRA_BOLD
    
    import pytest
    
    # Invalid string should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        text.font_weight("invalid-weight")
    assert "Invalid font weight" in str(excinfo.value)
