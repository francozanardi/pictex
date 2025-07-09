import pytest
from pathlib import Path
import tempfile
import os

from pictex import Canvas, SolidColor, LinearGradient, FontWeight, CropMode, Image

ASSETS_DIR = Path(__file__).parent / "assets"
STATIC_FONT_1_PATH = ASSETS_DIR / "static-font-1.ttf"

def check_regression(file_regression, image: Image):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_filename = tmp_file.name
    try:
        image.save(tmp_filename)
        with open(tmp_filename, 'rb') as f:
            file_content = f.read()
        
        file_regression.check(file_content, extension=".png", binary=True)
    finally:
        os.remove(tmp_filename)


def test_canvas_fluent_api_and_style_building():
    """
    Verifies that the fluent API correctly builds the underlying Style object.
    This is a smoke test to ensure the configuration works.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(50)
        .font_weight(FontWeight.BOLD)
        .color("#FF0000")
        .padding(10, 20)
    )
    
    style = canvas._style
    assert style.font.family == "Arial"
    assert style.font.size == 50
    assert style.font.weight == FontWeight.BOLD
    assert style.color == SolidColor.from_hex("#FF0000")
    assert style.padding == (10, 20, 10, 20)

@pytest.mark.parametrize("text, align", [
    ("Basic Text", "left"),
    ("Centered\nMulti-line", "center"),
    ("Right Aligned\nLonger First Line", "right")
])
def test_render_basic_text_and_alignment(file_regression, text, align):
    """Tests basic rendering and alignment."""
    canvas = Canvas().font_family("Arial").alignment(align)
    image = canvas.render(text)
    check_regression(file_regression, image)

def test_render_with_padding_and_background(file_regression):
    """Tests padding and a background with rounded corners."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .padding(20, 40)
        .background_color("#3498db")
        .background_radius(15)
        .color("white")
    )
    image = canvas.render("Padded Text")
    check_regression(file_regression, image)

def test_render_with_shadows_and_stroke(file_regression):
    """Tests visual effects like shadows and outline stroke."""
    canvas = (
        Canvas()
        .font_family("Impact")
        .font_size(80)
        .color("#f1c40f")
        .add_shadow(offset=(3, 3), blur_radius=5, color="#00000080")
        .add_box_shadow(offset=(10, 10), blur_radius=15, color="#00000050")
        .outline_stroke(width=4, color="black")
    )
    image = canvas.render("EFFECTS!")
    check_regression(file_regression, image)

def test_render_with_decorations(file_regression):
    """Tests text decorations like underline."""
    canvas = (
        Canvas()
        .font_family("Georgia")
        .font_size(60)
        .underline(thickness=3, color="red")
        .strikethrough(thickness=2)
    )
    image = canvas.render("Decorated")
    check_regression(file_regression, image)

def test_render_with_gradient(file_regression):
    """Tests the use of a linear gradient as a color source."""
    gradient = LinearGradient(colors=["#ff00ff", "#00ffff"])
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_weight(FontWeight.BOLD)
        .font_size(100)
        .color(gradient)
    )
    image = canvas.render("Gradient")
    check_regression(file_regression, image)

def test_render_with_custom_font(file_regression):
    """Tests loading a font from a .ttf file."""
    assert STATIC_FONT_1_PATH.exists(), "Test font file is missing"
    
    canvas = Canvas().font_family(str(STATIC_FONT_1_PATH)).font_size(70)
    image = canvas.render("Custom Font")
    check_regression(file_regression, image)

def test_render_with_smart_crop(file_regression):
    """Tests that the SMART crop mode works correctly."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .add_shadow((10, 10), 15, "#000") # Large shadow to create extra space
    )
    image = canvas.render("SMART", crop_mode=CropMode.SMART)
    check_regression(file_regression, image)
