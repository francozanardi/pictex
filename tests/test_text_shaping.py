from pictex import Canvas, NamedColor
from .conftest import FONT_WITH_LIGATURES_PATH

# TODO: vector image is actually not working for ligatures
def test_ligature_rendering(file_regression, render_engine):
    """
    Tests that ligatures are properly rendered when using a font that supports them.
    Characters like '->' and '==' should be rendered as single ligature glyphs.
    """
    canvas = (
        Canvas()
        .font_family(FONT_WITH_LIGATURES_PATH)
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "-> ==")
    check_func(file_regression, image)

def test_kerning_support(file_regression, render_engine):
    """
    Tests that kerning is properly applied to character pairs.
    Characters like 'AV' and 'TY' should have adjusted spacing between them.
    """
    canvas = (
        Canvas()
        .font_family("Impact")
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "AV TY")
    check_func(file_regression, image)

# TODO: vector image is actually not working for this complex emoji
def test_complex_emoji_rendering(file_regression, render_engine):
    """
    Tests that complex emoji sequences (like woman scientist) are properly rendered
    as a single glyph instead of separate emoji characters.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "👩‍🔬")
    check_func(file_regression, image)

def test_arabic_text_shaping(file_regression, render_engine):
    """
    Tests that Arabic text is properly shaped and rendered with correct
    character connections and forms.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "كتاب")
    check_func(file_regression, image)

# TODO: vector image is actually not working for this complex emoji
def test_family_emoji_with_zwj(file_regression, render_engine):
    """
    Tests that the family emoji (👨‍👩‍👧‍👦) composed with ZWJ (Zero Width Joiner)
    is properly rendered as a single glyph. The emoji is composed of:
    - 👨 (man)
    - U+200D (ZWJ)
    - 👩 (woman)
    - U+200D (ZWJ)
    - 👧 (girl)
    - U+200D (ZWJ)
    - 👦 (boy)
    
    HarfBuzz should combine these into a single family glyph, with ZWJ having width 0.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    # Family emoji: man + ZWJ + woman + ZWJ + girl + ZWJ + boy
    image = render_func(canvas, "👨‍👩‍👧‍👦")
    check_func(file_regression, image)

def test_emoji_with_modifiers(file_regression, render_engine):
    """
    Tests that emoji with skin tone modifiers render correctly.
    The skin tone modifier uses ZWJ to combine with the base emoji.
    
    Example: 👋🏽 (waving hand + medium skin tone)
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
    )
    render_func, check_func = render_engine
    # Waving hand emoji with medium skin tone modifier
    # 👋 (U+1F44B) + 🏽 (U+1F3FD skin tone modifier)
    image = render_func(canvas, "Hello 👋🏽 World")
    check_func(file_regression, image)

def test_multi_font_metrics_and_decorations(file_regression, render_engine):
    """
    Tests that elements with mixed fonts (e.g., standard text and tall fallback emojis)
    correctly calculate the common line height, baseline alignment, and underline position 
    based on all fonts in the line, rather than just the primary font.

    **NOTE**: The Noto Color Emoji font has a very large underline position, so there will be a blank space below the text.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .font_family("Arial")
        .color(NamedColor.BLUE)
        .background_color(NamedColor.BEIGE)
        .padding(20)
        .underline(thickness=10.0, color=NamedColor.RED)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, "Hello World 🛒🧗🚚")
    check_func(file_regression, image)
