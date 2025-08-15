import pytest
from pictex import Canvas, Row, Column, Text

ROW_CHILDREN = [
    Text("A").font_size(20).background_color("#3498db").padding(10),
    Row(Text("B")).font_size(40).background_color("#e74c3c").padding(10),
    Text("C").font_size(30).background_color("#2ecc71").padding(10),
]

COLUMN_CHILDREN = [
    Text("Short").background_color("#3498db").padding(10),
    Text("Loooooooooong").background_color("#e74c3c").padding(10),
    Text("Meeedium").background_color("#2ecc71").padding(10),
]

def test_row_default_layout(file_regression, render_engine):
    test_case = Row(*ROW_CHILDREN)
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

@pytest.mark.parametrize("mode", [
    "left", "center", "right", "space-between", "space-around", "space-evenly"
])
def test_row_horizontal_distribution(file_regression, render_engine, mode):
    test_case = (
        Row(*ROW_CHILDREN)
        .size(width=600)
        .background_color("#ecf0f1")
        .horizontal_distribution(mode)
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

@pytest.mark.parametrize("mode", ["top", "center", "bottom", "stretch"])
def test_row_vertical_alignment(file_regression, render_engine, mode):
    test_case = (
        Row(*ROW_CHILDREN)
        .size(height=150)
        .background_color("#ecf0f1")
        .vertical_align(mode)
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

def test_row_with_gap(file_regression, render_engine):
    test_case = Row(*ROW_CHILDREN).gap(20)
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

def test_row_with_gap_and_distribution(file_regression, render_engine):
    test_case = (
        Row(*ROW_CHILDREN)
        .size(width=800)
        .background_color("#ecf0f1")
        .gap(20)
        .horizontal_distribution('space-around')
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

def test_column_default_layout(file_regression, render_engine):
    test_case = Column(*COLUMN_CHILDREN)
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

@pytest.mark.parametrize("mode", [
    "top", "center", "bottom", "space-between", "space-around", "space-evenly"
])
def test_column_vertical_distribution(file_regression, render_engine, mode):
    test_case = (
        Column(*COLUMN_CHILDREN)
        .size(height=500)
        .background_color("#ecf0f1")
        .vertical_distribution(mode)
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

@pytest.mark.parametrize("mode", ["left", "center", "right", "stretch"])
def test_column_horizontal_alignment(file_regression, render_engine, mode):
    test_case = (
        Column(*COLUMN_CHILDREN)
        .size(width=300)
        .background_color("#ecf0f1")
        .horizontal_align(mode)
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

def test_column_with_gap(file_regression, render_engine):
    test_case = Column(*COLUMN_CHILDREN).gap(15)
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)

def test_column_with_gap_and_distribution(file_regression, render_engine):
    test_case = (
        Column(*COLUMN_CHILDREN)
        .size(height=600)
        .background_color("#ecf0f1")
        .gap(15)
        .vertical_distribution('space-between')
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)
