from pictex import Canvas, Row, LinearGradient

def test_border_style_dashed(file_regression, render_engine):
    """
    Tests a dashed border style.
    """
    render_func, check_func = render_engine

    element = (
        Row()
        .size(300, 150)
        .padding(20)
        .background_color("#ecf0f1")
        .border(width=8, color="#3498db", style='dashed')
        .border_radius(20)
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_border_style_dotted(file_regression, render_engine):
    """
    Tests a dotted border style.
    """
    render_func, check_func = render_engine

    element = (
        Row()
        .size(300, 150)
        .padding(20)
        .background_color("#f1c40f")
        .border(width=10, color="#2c3e50", style='dotted')
        .border_radius("50%")
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)


def test_border_with_gradient_color(file_regression, render_engine):
    """
    Verifies that a gradient can be used as the border color.
    """
    render_func, check_func = render_engine

    border_gradient = LinearGradient(
        colors=["#ff00cc", "#333399"],
        start_point=(0, 0),
        end_point=(1, 1)
    )

    element = (
        Row()
        .size(400, 200)
        .padding(20)
        .background_color("white")
        .border(width=15, color=border_gradient, style='solid')
        .border_radius(30)
    )

    image = render_func(Canvas(), element)
    check_func(file_regression, image)
