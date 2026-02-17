from pictex import Canvas, Row, Column, Text

def test_rtl_text_rendering(file_regression, render_engine):
    """
    Tests that RTL text (Arabic) renders correctly with direction("rtl").
    """
    canvas = (
        Canvas()
        .font_size(60)
        .padding(20)
    )
    # Using direction("rtl") with Arabic text
    text = Text("مرحبا بك").direction("rtl")
    
    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_ltr_text_rendering(file_regression, render_engine):
    """
    Tests that LTR text (English) renders correctly with direction("ltr").
    """
    canvas = (
        Canvas()
        .font_size(60)
        .padding(20)
    )
    text = Text("Hello World").direction("ltr")
    
    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_direction_inheritance(file_regression, render_engine):
    """
    Tests that text direction is properly inherited from parent containers.
    """
    # Parent column has direction("rtl")
    container = (
        Column(
            Text("Arabic Text 1").font_size(40),
            Text("Arabic Text 2").font_size(40),
        )
        .direction("rtl")
        .padding(20)
        .gap(10)
    )
    
    canvas = Canvas()
    render_func, check_func = render_engine
    image = render_func(canvas, container)
    check_func(file_regression, image)

def test_flex_row_direction_rtl(file_regression, render_engine):
    """
    Tests that a Row with direction("rtl") reverses the visual order of its children.
    In CSS, direction: rtl affects the start/end positions and item order in rows.
    """
    container = (
        Row(
            Text("Left").background_color("#3498db").padding(10),
            Text("Center").background_color("#e74c3c").padding(10),
            Text("Right").background_color("#2ecc71").padding(10),
        )
        .direction("rtl")
        .size(width=400)
        .gap(10)
        .padding(10)
    )
    
    canvas = Canvas()
    render_func, check_func = render_engine
    image = render_func(canvas, container)
    check_func(file_regression, image)

def test_mixed_direction_explicit(file_regression, render_engine):
    """
    Tests mixed directionality where some elements explicitly override the parent's direction.
    """
    container = (
        Column(
            Text("English (LTR Override)").direction("ltr").font_size(30),
            Text("العربية (RTL Override)").direction("rtl").font_size(30),
            Text("Inherited").font_size(30),
        )
        .direction("rtl")
        .padding(20)
        .gap(10)
    )
    
    canvas = Canvas()
    render_func, check_func = render_engine
    image = render_func(canvas, container)
    check_func(file_regression, image)
