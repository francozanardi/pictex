from pictex import Canvas
from .conftest import STATIC_FONT_PATH

def test_svg_with_embedded_font():
    """
    Tests that rendering an SVG with `embed_font=True` includes the
    @font-face and base64 data.
    """
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(50)

    vector_image = canvas.render_as_svg("Embed Test", embed_font=True)
    svg_content = vector_image.svg

    assert "<builders" in svg_content
    assert "@font-face" in svg_content
    assert "font-family: 'pictex-Lato'" in svg_content
    assert "src: url('data:font/ttf;base64," in svg_content
    assert "format('truetype')" in svg_content

def test_svg_without_embedded_font():
    """
    Tests that rendering an SVG with `embed_font=False` does NOT include
    the font data.
    """
    canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(50)
    vector_image = canvas.render_as_svg("No Embed Test", embed_font=False)
    svg_content = vector_image.svg

    assert "<builders" in svg_content
    assert "@font-face" in svg_content
    assert "base64" not in svg_content
    assert "font-family: 'pictex-Lato'" in svg_content
