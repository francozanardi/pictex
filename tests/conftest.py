import tempfile
import os
from pictex import Image, VectorImage, Canvas
from pathlib import Path
import pytest

ASSETS_DIR = Path(__file__).parent / "assets"
STATIC_FONT_PATH = str(ASSETS_DIR / "Lato-BoldItalic.ttf") # No emojies and japanese support
VARIABLE_WGHT_FONT_PATH = str(ASSETS_DIR / "Oswald-VariableFont_wght.ttf")
JAPANESE_FONT_PATH = str(ASSETS_DIR / "NotoSansJP-Regular.ttf")

def check_images_match(image_regression, image: Image):
    """
    Saves a pictex Image to a temporary file and checks it against a regression file.
    """
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_filename = tmp_file.name
    try:
        image.save(tmp_filename)
        with open(tmp_filename, 'rb') as f:
            file_content = f.read()
        
        image_regression.check(file_content, extension=".png", binary=True)
    finally:
        os.remove(tmp_filename)

def check_svgs_match(file_regression, vector_image: VectorImage):
    """Helper function to check SVG output against a baseline file."""
    file_regression.check(vector_image.svg, extension=".svg", encoding="utf-8")


@pytest.fixture(params=["raster", "vector"])
def render_engine(request):
    """
    A parametrized fixture that provides a render function and a check function
    for both raster (PNG) and vector (SVG) outputs.
    """
    render_mode = request.param

    if render_mode == "raster":
        def render_func(canvas: Canvas, text: str):
            return canvas.render(text)

        yield render_func, check_images_match

    elif render_mode == "vector":
        def render_func(canvas: Canvas, text: str):
            return canvas.render_as_svg(text, embed_font=False)

        yield render_func, check_svgs_match