from pictex import Canvas, Shadow

def test_render_with_simple_text_shadow(file_regression, render_engine):
    """
    Tests a single, basic drop shadow on text.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(120)
        .color("white")
        .padding(20)
        .text_shadows(Shadow(offset=(5, 5), blur_radius=10, color="#000000A0"))
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Text Shadow")
    check_func(file_regression, image)

def test_render_with_simple_box_shadow(file_regression, render_engine):
    """
    Tests a single, basic drop shadow on the background container.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .color("black")
        .padding(30)
        .background_color("white")
        .border_radius(15)
        .box_shadows(Shadow(offset=(10, 10), blur_radius=20, color="#00000060"))
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Box Shadow")
    check_func(file_regression, image)

def test_render_with_multiple_text_shadows(file_regression, render_engine):
    """
    Verifies that multiple text shadows can be layered to create complex effects.
    This creates an "engraved" or "inset" look.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(120)
        .padding(20)
        .background_color("#AAA")
        .color("gray")
        .text_shadows(
            Shadow(offset=(3, 3), blur_radius=3, color="black"),
            Shadow(offset=(-3, -3), blur_radius=0, color="white")
        )
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "INSET")
    check_func(file_regression, image)

def test_render_with_multiple_box_shadows(file_regression, render_engine):
    """
    Verifies that multiple box shadows can be layered, for example, to create
    a soft outer glow combined with a harder drop shadow.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .padding(40)
        .background_color("white")
        .border_radius(15)
        .box_shadows(
            Shadow(offset=(5, 5), blur_radius=5, color="#00000040"),
            Shadow(offset=(0, 0), blur_radius=25, color="#3498DB80")
        )
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Layered Box")
    check_func(file_regression, image)

def test_text_and_box_shadows_together(file_regression, render_engine):
    """
    Tests the interaction of both text shadows and box shadows on the same element
    to ensure they are both rendered correctly without interference.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(100)
        .padding(40)
        .background_color("#EEEEEE")
        .border_radius(20)
        .color("#2c3e50")
        .text_shadows(Shadow(offset=(2, 2), blur_radius=2, color="red"))
        .box_shadows(Shadow(offset=(5, 5), blur_radius=3, color="#00000050"))
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Combined")
    check_func(file_regression, image)

def test_hard_shadow_without_blur(file_regression, render_engine):
    """
    Tests an edge case where blur_radius is zero, creating a hard-edged duplicate.
    This is useful for creating "3D" text effects.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(120)
        .color("#e74c3c")
        .padding(20)
        .text_shadows(
            Shadow(offset=(4, 4), blur_radius=0, color="#2980b9"),
            Shadow(offset=(8, 8), blur_radius=0, color="#8e44ad")
        )
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "RETRO")
    check_func(file_regression, image)
