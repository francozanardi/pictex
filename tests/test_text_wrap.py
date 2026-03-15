import pytest
from pictex import Canvas, Text, Column, Row
from .conftest import STATIC_FONT_PATH, FONT_WITH_LIGATURES_PATH, JAPANESE_FONT_PATH

# Long text for wrapping tests
LONG_TEXT = "This is a very long sentence that will demonstrate text wrapping behavior when placed inside containers with various width constraints and settings."

def test_text_wrap_normal_vs_nowrap(file_regression, render_engine):
    """Compare text wrapping enabled vs disabled in fixed width containers."""
    render_func, check_func = render_engine
    
    # Create two containers side by side - one with wrapping, one without
    wrapped_text = Text(LONG_TEXT).text_wrap("normal")
    wrapped_container = Column(wrapped_text).size(width=200).background_color("#E8F4FD").padding(10)
    
    nowrap_text = Text(LONG_TEXT).text_wrap("nowrap")
    nowrap_container = Column(nowrap_text).size(width=200).background_color("#FDE8E8").padding(10)
    
    layout = Row(wrapped_container, nowrap_container).gap(20)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(14)
    image = render_func(canvas, layout)
    check_func(file_regression, image)


def test_text_wrap_inherited_from_parent(file_regression, render_engine):
    """Test that text wrap style is inherited by child Text elements."""
    render_func, check_func = render_engine
    
    # Parent container with nowrap - children should inherit this
    no_wrap_container = Column(
        Text("Child 1: " + LONG_TEXT[:50]),
        Text("Child 2: " + LONG_TEXT[50:100]),
        Text("Child 3: " + LONG_TEXT[100:150]),
    ).text_wrap("nowrap").size(width=250).background_color("#FFF0E6").padding(10).gap(8)
    
    # Parent container with normal wrapping (default)
    wrap_container = Column(
        Text("Child A: " + LONG_TEXT[:50]),
        Text("Child B: " + LONG_TEXT[50:100]),
        Text("Child C: " + LONG_TEXT[100:150]),
    ).size(width=250).background_color("#E6FFE6").padding(10).gap(8)
    
    layout = Row(no_wrap_container, wrap_container).gap(20)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(12)
    image = render_func(canvas, layout)
    check_func(file_regression, image)


def test_text_wrap_override_inheritance(file_regression, render_engine):
    """Test that child elements can override inherited text wrap settings."""
    render_func, check_func = render_engine
    
    # Container with nowrap, but some children override to normal
    container = Column(
        Text("Inherits nowrap: " + LONG_TEXT[:60]),  # Uses parent's nowrap
        Text("Overrides to normal: " + LONG_TEXT[:60]).text_wrap("normal"),  # Overrides to wrap
        Text("Inherits nowrap again: " + LONG_TEXT[:60]),  # Uses parent's nowrap
        Text("Another override: " + LONG_TEXT[:60]).text_wrap("normal"),  # Overrides to wrap
    ).text_wrap("nowrap").size(width=300).background_color("#F0F0F0").padding(15).gap(10)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(13)
    image = render_func(canvas, container)
    check_func(file_regression, image)


@pytest.mark.parametrize("width", [150, 250, 350])
def test_text_wrap_different_widths(file_regression, render_engine, width):
    """Test text wrapping behavior with different container widths."""
    render_func, check_func = render_engine
    
    text_elem = Text(LONG_TEXT).background_color("#F5F5DC").padding(8)
    container = Column(text_elem).size(width=width).background_color("#DDD").padding(10)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(14)
    image = render_func(canvas, container)
    check_func(file_regression, image)


def test_text_wrap_with_multiline_text(file_regression, render_engine):
    """Test text wrapping combined with manual line breaks."""
    render_func, check_func = render_engine
    
    multiline_text = "First line with manual break.\nSecond line is longer and will demonstrate wrapping behavior.\nThird line is short.\nFourth line contains more text to show wrapping."
    
    # Compare wrapped vs nowrap with multiline text
    wrapped_elem = Text(multiline_text).text_wrap("normal")
    wrapped_container = Column(wrapped_elem).size(width=200).background_color("#E6F3FF").padding(10)
    
    nowrap_elem = Text(multiline_text).text_wrap("nowrap")
    nowrap_container = Column(nowrap_elem).size(width=200).background_color("#FFE6F3").padding(10)
    
    layout = Row(wrapped_container, nowrap_container).gap(20)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(12)
    image = render_func(canvas, layout)
    check_func(file_regression, image)


def test_text_wrap_with_percentage_width(file_regression, render_engine):
    """Test text wrapping in containers with percentage-based widths."""
    render_func, check_func = render_engine
    
    text_elem = Text(LONG_TEXT)
    # Inner container is 60% of outer (300px), so 180px effective width
    inner_container = Column(text_elem).size(width="60%").background_color("#F0FFFF").padding(10)
    outer_container = Column(inner_container).size(width=300).background_color("#F5F5F5").padding(15)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(13)
    image = render_func(canvas, outer_container)
    check_func(file_regression, image)


def test_text_wrap_nested_containers(file_regression, render_engine):
    """Test text wrapping in deeply nested container structures."""
    render_func, check_func = render_engine
    
    text_elem = Text(LONG_TEXT[:80])  # Shorter text for nested example
    
    # Create nested structure with decreasing widths
    level1 = Column(text_elem).size(width="90%").background_color("#FFE6E6").padding(8)
    level2 = Column(level1).size(width="80%").background_color("#E6E6FF").padding(8)
    level3 = Column(level2).size(width="70%").background_color("#E6FFE6").padding(8)
    level4 = Column(level3).size(width=400).background_color("#FFFFCC").padding(10)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(12)
    image = render_func(canvas, level4)
    check_func(file_regression, image)


def test_text_wrap_with_styling(file_regression, render_engine):
    """Test that text wrapping works correctly with other text styling options."""
    render_func, check_func = render_engine
    
    styled_text = (Text(LONG_TEXT[:100])
                   .font_size(16)
                   .color("#2C3E50")
                   .line_height(1.4)
                   .text_align("center")
                   .background_color("#ECF0F1")
                   .padding(12))
    
    container = Column(styled_text).size(width=280).background_color("#BDC3C7").padding(15)
    
    canvas = Canvas().font_family(STATIC_FONT_PATH)
    image = render_func(canvas, container)
    check_func(file_regression, image)

def test_no_false_wrap_without_width_constraint(file_regression, render_engine):
    """Text should not word-wrap when no width is set on the canvas or container.

    With a monospace font (FiraCode) at size 35, the 15-glyph
    text "shipment cdncdi" has an advance width that triggers a floating-point
    mismatch between the intrinsic width measurement path (which passed through
    skia.Rect float32) and the wrapping logic (float64). This caused text to
    wrap even when it fit on a single line.
    """
    render_func, check_func = render_engine

    canvas = (
        Canvas()
        .font_family(FONT_WITH_LIGATURES_PATH)
        .font_size(35)
        .background_color("#ffffff")
        .padding(25)
    )
    image = render_func(canvas, "shipment cdncdi")
    check_func(file_regression, image)


def test_cjk_text_wraps_within_fixed_width(file_regression, render_engine):
    """CJK text should wrap character-by-character within a fixed-width container.

    CJK characters don't have spaces between them, so the
    tokenizer must treat each character as an individual breakable unit.
    Without this, a long CJK string is treated as a single unbreakable word
    and overflows the container instead of wrapping.
    """
    render_func, check_func = render_engine

    cjk_text = Text(
        "これはテスト用の日本語テキストです。文字ごとに改行できるか確認します。"
    ).font_size(30).color("blue")

    container = Column(cjk_text).font_family(JAPANESE_FONT_PATH).size(width=512, height=128).padding(10)

    canvas = Canvas().background_color("white")
    image = render_func(canvas, container)
    check_func(file_regression, image)


def test_two_sibling_texts_using_width_limited_by_ancestor(file_regression, render_engine):
    render_func, check_func = render_engine
    ONE_LONG_WORD = "OneLongWord"

    one_long_word = Column(Text(ONE_LONG_WORD).font_weight(700)).border(3, "blue")
    long_text = Column(Text(LONG_TEXT).font_weight(700)).border(3, "red")

    container = Row(
        one_long_word,
        long_text
    ).padding(20).background_color("white").border_radius(10).size(width=700)

    canvas = Canvas().background_color("#DAE0E6").padding(40)
    image = render_func(canvas, container)
    check_func(file_regression, image)
