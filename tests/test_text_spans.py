from pictex import Canvas, Text, Span, LinearGradient, TextDecoration, OutlineStroke, Shadow

def test_span_basic_color(file_regression, render_engine):
    """Verifies that a basic solid color override on a span works correctly."""
    canvas = Canvas().padding(20).font_size(60)
    text = Text(
        "This is ",
        Span("red").color("red"),
        " text."
    )
    
    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_nested_inheritance(file_regression, render_engine):
    """Ensures that a nested span inherits properties like color from its parent span."""
    canvas = Canvas().padding(20)
    text = Text(
        Span(
            "Outer green, ",
            Span("Inner bold green.").font_weight("bold")
        ).color("green")
    ).font_size(60)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_gradient_across_subspans(file_regression, render_engine):
    """Tests that a gradient applied to an outer span stretches correctly across internal subspans."""
    gradient = LinearGradient(colors=["red", "blue"])
    canvas = Canvas().padding(40)
    text = Text(
        Span(
            "Gradient start. ",
            Span("Middle bold. ").font_weight("bold"),
            "Gradient end."
        ).color(gradient)
    ).font_size(80).font_family("Arial")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_gradient_with_implicit_text(file_regression, render_engine):
    """Checks that a gradient applied to the text block behaves as expected around spans with overriding colors."""
    gradient = LinearGradient(colors=["yellow", "purple"])
    canvas = Canvas().padding(40).background_color("#111111")
    text = Text(
        "Text block gradient. ",
        Span("Span solid color. ").color("green"),
        "Text block gradient again."
    ).color(gradient).font_size(60).font_weight("bold")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_multiline_gradient(file_regression, render_engine):
    """Verifies that a vertical gradient stretches accurately across multiple lines inside a single span."""
    gradient = LinearGradient(colors=["red", "blue"], start_point=(0, 0), end_point=(0, 1))
    canvas = Canvas().padding(20)
    text = Text(
        Span(
            "Line 1 of the gradient\n",
            "Line 2 of the gradient\n",
            Span("Line 3 with custom font size").font_size(40)
        ).color(gradient)
    ).font_size(80)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_continuous_underline(file_regression, render_engine):
    """Ensures that identical underline properties merge into a single continuous segment across subspans."""
    canvas = Canvas().padding(20)
    text = Text(
        Span(
            "Continuous ",
            Span("underline ").color("blue"),
            Span("across ").font_weight("bold"),
            "spans."
        ).underline(thickness=4)
    ).font_size(60).color("black")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_distinct_underlines(file_regression, render_engine):
    """Tests that separate consecutive spans with different underline colors render as distinct segments."""
    canvas = Canvas().padding(20)
    text = Text(
        Span("Red underline. ").underline(color="red", thickness=5),
        Span("Blue underline.").underline(color="blue", thickness=5)
    ).font_size(60).color("black")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_text_stroke_and_shadow(file_regression, render_engine):
    """Combines text stroke, shadow, and gradient fill simultaneously on a single subspan."""
    gradient = LinearGradient(colors=["orange", "purple"])
    canvas = Canvas().padding(40).background_color("#EEEEEE")
    text = Text(
        "Normal text. ",
        Span("Outlined and shadowed.").text_stroke(
            width=3, color="black"
        ).text_shadows(
            Shadow(color="#00000080", blur_radius=5, offset=(5, 5))
        ).color(gradient).font_weight(800)
    ).font_size(80).font_family("Arial")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_complex_nesting(file_regression, render_engine):
    """Validates deeply nested spans alternating between inheritance and explicit property overrides."""
    gradient = LinearGradient(colors=["green", "blue"])
    canvas = Canvas().padding(40)
    text = Text(
        Span(
            "Level 1 (Red). ",
            Span(
                "Level 2 (Gradient). ",
                Span(
                    "Level 3 (Gradient + Bold). "
                ).font_weight("bold"),
                "Back to Level 2. "
            ).color(gradient),
            "Back to Level 1."
        ).color("red")
    ).font_size(60).font_family("Arial")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_letter_spacing(file_regression, render_engine):
    """Ensures letter spacing within a span computes layout dimensions and offsets accurately."""
    canvas = Canvas().padding(20)
    text = Text(
        "No space. ",
        Span("Wide space. ").letter_spacing(15),
        "No space."
    ).font_size(60)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_text_block_multiline_gradient(file_regression, render_engine):
    """Checks that a gradient applied to a multi-line Text block accurately spans the entire block's bounds."""
    gradient = LinearGradient(colors=["purple", "orange"], start_point=(0, 0), end_point=(1, 1))
    canvas = Canvas().padding(40)
    text = Text(
        "Line 1 with text block gradient\n"
        "Line 2 with text block gradient\n"
        "Line 3 with text block gradient"
    ).color(gradient).font_size(60).font_weight("bold")

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_wrap_multiline_gradient_with_width(file_regression, render_engine):
    """
    Tests text wrapping dynamically caused by width constraints (no raw '\n'), ensuring the 
    origin_id gradient bounds correctly span precisely across all dynamically generated lines.
    """
    gradient = LinearGradient(colors=["purple", "orange"], start_point=(0, 0), end_point=(0, 1))
    canvas = Canvas().padding(40).width(800)
    text = Text(
        "Start of normal text block that is boring. ",
        Span(
            "This is a massive block of span text that will inevitably wrap around the edges "
            "multiple times until it forms several distinct layout lines, computing a huge "
            "vertical and horizontal bounding box for its gradient. "
        ).color(gradient).font_weight("bold"),
        "And back to boring baseline text."
    ).font_size(60)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_inline_emoji_gradient(file_regression, render_engine):
    """
    Places emojis inline (e.g. text emoji text) within a span to force multiple shaping runs 
    without causing line breaks, validating exact horizontal union of bounds for the gradient.
    """
    from pictex import SweepGradient
    gradient = SweepGradient(colors=["red", "yellow", "cyan", "blue", "magenta"])
    canvas = Canvas().padding(40)
    text = Text(
        "Normal: ",
        Span("Start 🧪 Middle 🚀 End!").color(gradient).font_weight("bold").font_size(80),
        " Done."
    ).font_size(60)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_inherited_gradient_underline_with_runs(file_regression, render_engine):
    """
    Tests that a decoration without explicit color inherits the text's gradient 
    and perfectly maps it over the span's bounds, mixed with emojis that force multiple text shaping runs.
    """
    gradient = LinearGradient(colors=["red", "yellow"], start_point=(0, 0), end_point=(1, 0))
    canvas = Canvas().padding(40)
    text = Text(
        "Context. ",
        Span(
            "This 👍 is 😎 a 🎉 gradient span."
        ).color(gradient),
        " End context."
    ).font_size(60).underline(thickness=6)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_arabic_contextual_joining(file_regression, render_engine):
    """
    Validates that Arabic characters contextually join correctly even when split across different spans.
    The word 'كتاب' (kitab) is split. 'ت' must join contextually with 'ا' despite the color transition.
    """
    from .conftest import VAZIRMATN_FONT_PATH
    canvas = Canvas().padding(40)
    text = Text(
        Span("كت").color("red"), 
        Span("اب").color("blue")
    ).font_size(120).font_family(VAZIRMATN_FONT_PATH)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_variable_font_sizes(file_regression, render_engine):
    """
    Mixes drastically different font sizes within spans in a single line. The gradient bounds 
    on the smaller text should still align with the line's max height established by the large text.
    """
    gradient = LinearGradient(colors=["blue", "green"], start_point=(0, 0), end_point=(0, 1))
    canvas = Canvas().padding(40)
    text = Text(
        Span(
            "Tiny ",
            Span("HUGE").font_size(180),
            " tiny"
        ).color(gradient)
    ).font_size(40)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)

def test_span_bidi_reordering_with_gradient(file_regression, render_engine):
    """
    Combines nested spans, gradients, and bidirectional text reordering. Validates bounding box 
    computation maps accurately to the visual (reordered) coordinates rather than logical coordinates.
    """
    from .conftest import VAZIRMATN_FONT_PATH
    gradient = LinearGradient(colors=["black", "white"], start_point=(0, 0), end_point=(1, 0))
    canvas = Canvas().padding(40).background_color("#777777")
    
    # Text will visually reorder to: "Start: عربى (Arabic) !"
    text = Text(
        "Start: ",
        Span("عربى (").color("orange"),
        Span("Arabic").color(gradient).font_weight("bold"),
        Span(") !").color("orange")
    ).font_size(80).font_family(VAZIRMATN_FONT_PATH)

    render_func, check_func = render_engine
    image = render_func(canvas, text)
    check_func(file_regression, image)
