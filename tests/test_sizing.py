import pytest
from pictex import Canvas, Row, Column, Text, Image, Box
from .conftest import IMAGE_PATH

def test_size_absolute(file_regression, render_engine):
    """
    Tests that an element with an absolute size is rendered with the exact
    specified dimensions. The background color helps visualize the bounds.
    """
    render_func, check_func = render_engine

    element = Row(Text("Fixed Size")).size(width=400, height=150).background_color("#3498db")

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_size_fit_content_on_text(file_regression, render_engine):
    """
    Tests that a Text element with 'fit-content' (the default behavior)
    wraps its content precisely.
    """
    render_func, check_func = render_engine

    # 'fit-content' is the default, so we don't need to call .size()
    element = Text("Fit Content").background_color("#2ecc71").padding(10)

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_size_fit_content_on_row(file_regression, render_engine):
    """
    Tests that a Row with 'fit-content' correctly calculates its size
    based on the combined layout size of its children.
    """
    render_func, check_func = render_engine

    element = Row(
        Text("First").padding(10).background_color("#f1c40f"),
        Text("Second").padding(10).margin(0, 0, 0, 20).background_color("#e67e22")
    ).background_color("#34495e")

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_size_fit_background_image(file_regression, render_engine):
    """
    Tests that an element with '.fit_background_image()' takes on the
    dimensions of its background image (e.g., 300x200).
    """
    render_func, check_func = render_engine

    element = (
        Row("The row has the size of the image")
        .background_image(IMAGE_PATH)
        .fit_background_image()
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_size_percent_width_and_fixed_height(file_regression, render_engine):
    """
    Tests a child with a percentage-based width inside a parent with a
    fixed size. The child should take up 50% of the parent's content area.
    """
    render_func, check_func = render_engine

    parent = Column(
        Text("50% Width").size(width="50%", height=50).background_color("#9b59b6")
    ).size(
        width=400, height=200
    ).padding(
        20
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), parent)
    check_func(file_regression, image)


def test_size_percent_height(file_regression, render_engine):
    """
    Tests a child with a percentage-based height.
    """
    render_func, check_func = render_engine

    parent = Row(
        Text("25% Height").size(width=100, height="25%").background_color("#1abc9c")
    ).size(
        width=300, height=400
    ).padding(
        50, 0
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), parent)
    check_func(file_regression, image)


def test_size_percent_throws_error_on_fit_content_parent(render_engine):
    """
    Verifies that the system correctly raises a ValueError when a child
    with a percentage size is placed inside a parent with a 'fit-content'
    size, preventing an infinite loop.
    """
    render_func, _ = render_engine

    # This parent's size depends on its children.
    parent_with_fit_content = Row(
        # This child's size depends on its parent.
        Text("I cause a problem").size(width="50%")
    )  # No .size() means 'fit-content'

    with pytest.raises(ValueError, match="Cannot use 'percent' size if parent element has 'fit-content' size"):
        render_func(Canvas(), parent_with_fit_content)


def test_size_percent_on_root_element_is_not_supported(render_engine):
    """
    Verifies that using a percentage size on a root element, which has no
    container to be relative to, raises an error.
    """
    render_func, _ = render_engine

    canvas = Canvas().size(width="50%")

    with pytest.raises(ValueError, match="Cannot use 'percent' size on a root element without a parent"):
        render_func(canvas, "Percent")

def test_size_fill_available_single_child(file_regression, render_engine):
    """
    Tests that a single 'fill-available' child expands to fill all the
    remaining space in a Row next to a fixed-size sibling.
    """
    render_func, check_func = render_engine

    parent = Row(
        Image(IMAGE_PATH).size(width=100), # Fixed-size sibling takes 100px
        Text("This text fills the rest").size(width='fill-available').background_color("#27ae60"),
    ).size(
        width=400, height=150
    ).gap(
        20
    ).padding(
        10
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), parent)
    check_func(file_regression, image)


def test_size_fill_available_multiple_children(file_regression, render_engine):
    """
    Tests that multiple 'fill-available' children share the remaining
    space equally.
    """
    render_func, check_func = render_engine

    parent = Column(
        Text("Fixed Top").size(height=50).background_color("#f39c12"),
        Row(Text("Flexible 1")).size(height='fill-available').background_color("#2980b9"),
        Row(Text("Flexible 2")).size(height='fill-available').background_color("#8e44ad"),
        Text("Fixed Bottom").size(height=30).background_color("#f39c12"),
    ).size(
        width=300, height=400
    ).gap(
        10
    ).padding(
        20
    ).background_color("#ecf0f1")
    
    image = render_func(Canvas(), parent)
    check_func(file_regression, image)
