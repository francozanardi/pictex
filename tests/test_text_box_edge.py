import pytest
from pictex import Canvas, Column, Text
from pictex import TextBoxEdge, TextBoxEdgeValue


def test_text_box_edge_builder_both():
    text = Text("hello")
    text.text_box_edge("glyphs")
    assert text._style.text_box_edge == TextBoxEdge(
        top=TextBoxEdgeValue.GLYPHS,
        bottom=TextBoxEdgeValue.GLYPHS,
    )


def test_text_box_edge_builder_kwargs():
    text = Text("hello")
    text.text_box_edge(top="glyphs", bottom="font")
    assert text._style.text_box_edge == TextBoxEdge(
        top=TextBoxEdgeValue.GLYPHS,
        bottom=TextBoxEdgeValue.FONT,
    )


def test_text_box_edge_builder_enum_values():
    text = Text("hello")
    text.text_box_edge(TextBoxEdgeValue.GLYPHS)
    assert text._style.text_box_edge == TextBoxEdge(
        top=TextBoxEdgeValue.GLYPHS,
        bottom=TextBoxEdgeValue.GLYPHS,
    )


def test_text_box_edge_builder_raises_on_mixed_args():
    with pytest.raises(TypeError):
        Text("hello").text_box_edge("glyphs", top="font")  # type: ignore[call-overload]


def test_text_box_edge_builder_raises_on_missing_args():
    with pytest.raises(TypeError):
        Text("hello").text_box_edge()  # type: ignore[call-overload]


def test_text_box_edge_all_modes(file_regression, render_engine):
    """
    Renders four Text nodes side by side showing all text_box_edge combinations:
    - both glyphs
    - top glyphs, bottom font
    - top font, bottom glyphs
    - both font (default)
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(100)
        .background_color("pink")
    )
    content = Column(
        Text("hello").text_box_edge("glyphs").border(10, "red").background_color("cyan"),
        Text("hello").text_box_edge(top="glyphs", bottom="font").border(10, "red").background_color("cyan"),
        Text("hello").text_box_edge(top="font", bottom="glyphs").border(10, "red").background_color("cyan"),
        Text("hello").text_box_edge("font").border(10, "red").background_color("cyan"),
    ).gap(10)
    render_func, check_func = render_engine
    image = render_func(canvas, content)
    check_func(file_regression, image)


def test_text_box_edge_glyphs_with_line_height(file_regression, render_engine):
    """
    Tests that text_box_edge("glyphs") works correctly when combined with
    an explicit line_height multiplier.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .background_color("pink")
        .line_height(1.5)
    )
    content = Column(
        Text("pgÝÁ").text_box_edge("glyphs").border(10, "red").background_color("cyan"),
        Text("pgÝÁ").text_box_edge("font").border(10, "red").background_color("cyan"),
    ).gap(10)
    render_func, check_func = render_engine
    image = render_func(canvas, content)
    check_func(file_regression, image)


def test_text_box_edge_with_emojis(file_regression, render_engine):
    """
    Tests text_box_edge with text that contains emojis, which produce multiple
    text runs (emoji font fallback) within a single Text node.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .background_color("pink")
    )
    content = Column(
        Text("hello 🎉 world").text_box_edge("glyphs").border(10, "red").background_color("cyan"),
        Text("hello 🎉 world").text_box_edge("font").border(10, "red").background_color("cyan"),
        Text("🔥🎨✨").text_box_edge("glyphs").border(10, "red").background_color("cyan"),
        Text("🔥🎨✨").text_box_edge("font").border(10, "red").background_color("cyan"),
    ).gap(10)
    render_func, check_func = render_engine
    image = render_func(canvas, content)
    check_func(file_regression, image)
