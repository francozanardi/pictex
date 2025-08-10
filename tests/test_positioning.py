from pictex import Canvas, Row, Column, Text, Image

def test_position_absolute_is_removed_from_row_flow(file_regression, render_engine):
    """
    Tests that an element with absolute positioning is ignored by the
    Row's layout algorithm. Text 'One' and 'Three' should appear
    next to each other as if 'Two' doesn't exist in the flow.
    """
    render_func, check_func = render_engine

    element = Row(
        Text("One").padding(10).background_color("#3498db"),
        Text("Two")
        .absolute_position("center", "center")  # This element is out of the layout flow.
        .padding(10)
        .background_color("#e74c3c"),
        Text("Three").padding(10).background_color("#2ecc71"),
    ).size(
        width=400, height=150  # Give the parent a fixed size for stable positioning.
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_position_absolute_is_removed_from_column_flow(file_regression, render_engine):
    """
    Tests that an element with absolute positioning is ignored by the
    Column's layout algorithm. The logic is the same as for Row, but
    on the vertical axis.
    """
    render_func, check_func = render_engine

    element = Column(
        Text("One").padding(10).background_color("#3498db"),
        Text("Two")
        .absolute_position("center", "center")
        .padding(10)
        .background_color("#e74c3c"),
        Text("Three").padding(10).background_color("#2ecc71"),
    ).size(
        width=200, height=300
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_position_anchors_and_offsets(file_regression, render_engine):
    """
    Tests various combinations of anchor keywords and pixel offsets to ensure
    the positioning calculations are correct relative to the parent container.
    """
    render_func, check_func = render_engine

    container = Row(
        Text("TL").position("left", "top").background_color("#1abc9c"),
        Text("TR").position("right", "top").background_color("#1abc9c"),
        Text("BL").position("left", "bottom").background_color("#1abc9c"),
        Text("BR").position("right", "bottom").background_color("#1abc9c"),
        Text("Center").position("center", "center").background_color("#9b59b6"),
        Text("Offset").position(
            "left", "top", x_offset=50, y_offset=50
        ).background_color("#f1c40f"),
    ).size(
        width=300, height=200
    ).padding(
        10
    ).background_color("#bdc3c7")

    image = render_func(Canvas(), container)
    check_func(file_regression, image)


def test_position_with_percentages(file_regression, render_engine):
    """

    Tests that percentage-based positions are calculated correctly based on
    the parent's content-box dimensions.
    """
    render_func, check_func = render_engine

    container = Column(
        Text("25% x, 75% y").position("25%", "75%").background_color("#e67e22")
    ).size(
        width=400, height=300
    ).padding(
        50
    ).background_color("#ecf0f1")

    image = render_func(Canvas(), container)
    check_func(file_regression, image)


def test_position_with_mixed_anchors(file_regression, render_engine):
    """
    Tests that a combination of keyword and percentage anchors works as expected.
    Also tests the content anchor calculation (centering the element on the anchor point).
    """
    render_func, check_func = render_engine

    container = Row(
        Text("Centered on 50%, 20px")
        .position("50%", 20)
        .background_color("#34495e")
        .color("white")
        .padding(10)
    ).size(
        width=500, height=200
    ).background_color("#ecf0f1")

    # In this case, '50%' means the *left edge* of the child is at the 50% mark.
    # The 'center' keyword, however, aligns the *center* of the child. This test
    # helps distinguish and verify both anchor types.

    image = render_func(Canvas(), container)
    check_func(file_regression, image)

def test_container_with_position(file_regression, render_engine):
    render_func, check_func = render_engine
    
    container = Row(Column("test").absolute_position(0, 0)).size(100, 100)
    image = render_func(Canvas(), container)
    check_func(file_regression, image)