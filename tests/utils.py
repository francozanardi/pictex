import tempfile
import os
from pictex import Image
from pathlib import Path

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
