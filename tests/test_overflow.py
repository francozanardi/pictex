"""Visual regression tests for ``overflow: hidden``.

These tests verify that content clipping works correctly in both container
(Row/Column) and text nodes, that the background and border are never clipped,
and that baseline (overflow: visible) behaviour is unchanged.
"""
from pictex import Canvas, Row, Column, Text


# ---------------------------------------------------------------------------
# overflow: hidden on containers
# ---------------------------------------------------------------------------

def test_overflow_hidden_row_clips_children(file_regression, render_engine):
    """Children that exceed the Row's fixed width are clipped."""
    test_case = (
        Row(
            Text("Short").font_size(30).background_color("#3498db").padding(8),
            Text("This text is very wide").font_size(30).background_color("#e74c3c").padding(8),
            Text("Also wide item").font_size(30).background_color("#2ecc71").padding(8),
        )
        .size(width=500)
        .text_wrap("nowrap")
        .background_color("#ecf0f1")
        .overflow("hidden")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


def test_overflow_hidden_column_clips_children(file_regression, render_engine):
    """Children that exceed the Column's fixed height are clipped."""
    test_case = (
        Column(
            Text("Line 1").font_size(30).background_color("#3498db").padding(8),
            Text("Line 2").font_size(30).background_color("#e74c3c").padding(8),
            Text("Line 3").font_size(30).background_color("#2ecc71").padding(8),
            Text("Line 4 - hidden").font_size(30).background_color("#9b59b6").padding(8),
        )
        .size(height=120 + 8*2*3)
        .background_color("#ecf0f1")
        .overflow("hidden")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


def test_overflow_visible_row_does_not_clip(file_regression, render_engine):
    """Baseline: with overflow visible, children bleed outside the container."""
    test_case = (
        Row(
            Text("Short").font_size(30).background_color("#3498db").padding(8),
            Text("This text is very wide").font_size(30).background_color("#e74c3c").padding(8),
            Text("Also wide item").font_size(30).background_color("#2ecc71").padding(8),
        )
        .size(width=500)
        .text_wrap("nowrap")
        .background_color("#ecf0f1")
        .overflow("visible")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


# ---------------------------------------------------------------------------
# overflow: hidden on text nodes
# ---------------------------------------------------------------------------

def test_overflow_hidden_text_clips_content(file_regression, render_engine):
    """Long text that would overflow a fixed-size box is clipped."""
    test_case = (
        Text("This is a very long sentence that will overflow the fixed box.")
        .font_size(24)
        .color("blue")
        .size(width=200, height=60)
        .background_color("#ecf0f1")
        .overflow("hidden")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


def test_overflow_visible_text_does_not_clip(file_regression, render_engine):
    """Baseline: without overflow hidden, long text overflows the fixed box."""
    test_case = (
        Text("This is a very long sentence that will overflow the fixed box.")
        .font_size(24)
        .color("blue")
        .size(width=200, height=60)
        .background_color("#ecf0f1")
        .overflow("visible")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


# ---------------------------------------------------------------------------
# overflow: hidden + border — border must not be clipped
# ---------------------------------------------------------------------------

def test_overflow_hidden_preserves_border(file_regression, render_engine):
    """The element border must remain fully visible even with overflow: hidden."""
    test_case = (
        Row(
            Text("Content A").font_size(28).background_color("#3498db").padding(8),
            Text("Content B - overflows").font_size(28).background_color("#e74c3c").padding(8),
        )
        .size(width=200)
        .background_color("#ecf0f1")
        .border(4, "#2c3e50")
        .overflow("hidden")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)


def test_overflow_hidden_preserves_border_radius(file_regression, render_engine):
    """overflow: hidden + border-radius clips children to the rounded rect."""
    test_case = (
        Row(
            Text("A").font_size(36).background_color("#3498db").padding(12),
            Text("B").font_size(36).background_color("#e74c3c").padding(12),
            Text("C").font_size(36).background_color("#2ecc71").padding(12),
        )
        .size(width=150)
        .background_color("#ecf0f1")
        .border_radius(20)
        .border(4, "#2c3e50")
        .overflow("hidden")
    )
    render_func, check_func = render_engine
    image = render_func(Canvas(), test_case)
    check_func(file_regression, image)
