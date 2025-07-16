import pytest
import numpy as np
import skia
from pictex import Image, Box

@pytest.fixture
def dummy_skia_image():
    """Creates a simple 2x2 red skia.Image for testing."""
    pixels = np.array([
        [[0, 0, 255, 255], [0, 0, 255, 255]],
        [[0, 0, 255, 255], [0, 0, 255, 255]],
    ], dtype=np.uint8)

    return skia.Image.fromarray(pixels)

def test_image_properties(dummy_skia_image):
    """Tests the basic properties of the Image class."""
    content_box = Box(x=10, y=20, width=30, height=40)
    image = Image(skia_image=dummy_skia_image, content_box=content_box)

    assert image.width == 2
    assert image.height == 2
    assert image.content_box == content_box
    assert image.skia_image is dummy_skia_image
    assert isinstance(image, Image)

def test_image_to_numpy(dummy_skia_image):
    """Tests the to_numpy() conversion method."""
    image = Image(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))

    numpy_bgra = image.to_numpy(rgba=False)
    assert numpy_bgra.shape == (2, 2, 4)
    assert np.array_equal(numpy_bgra[0, 0], [0, 0, 255, 255])
    numpy_rgba = image.to_numpy(rgba=True)
    assert numpy_rgba.shape == (2, 2, 4)
    assert np.array_equal(numpy_rgba[0, 0], [255, 0, 0, 255])

def test_image_to_bytes(dummy_skia_image):
    """Tests that to_bytes returns the expected raw bytes."""
    image = Image(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))

    expected_bytes = bytes([0, 0, 255, 255] * 4)
    assert image.to_bytes() == expected_bytes

def test_image_to_pillow(dummy_skia_image):
    """Tests conversion to a Pillow image."""
    from PIL import Image as PillowImage

    image = Image(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))
    pillow_image = image.to_pillow()

    assert isinstance(pillow_image, PillowImage.Image)
    assert pillow_image.size == (2, 2)
    assert pillow_image.mode == "RGBA"
    assert pillow_image.getpixel((0, 0)) == (255, 0, 0, 255)
