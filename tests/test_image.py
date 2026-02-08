import pytest
import numpy as np
import skia
from pictex import BitmapImage, Box, RenderNode, NodeType

@pytest.fixture
def dummy_skia_image():
    """Creates a simple 2x2 red skia.Image for testing."""
    pixels = np.array([
        [[0, 0, 255, 255], [0, 0, 255, 255]],
        [[0, 0, 255, 255], [0, 0, 255, 255]],
    ], dtype=np.uint8)

    return skia.Image.fromarray(pixels, colorType=skia.kBGRA_8888_ColorType)

def test_image_properties(dummy_skia_image):
    """Tests the basic properties of the Image class."""
    content_box = Box(x=10, y=20, width=30, height=40)
    image = BitmapImage(skia_image=dummy_skia_image, content_box=content_box)

    assert image.width == 2
    assert image.height == 2
    assert image.content_box == content_box
    assert image.skia_image is dummy_skia_image
    assert image.render_tree is None  # Default is None
    assert isinstance(image, BitmapImage)

def test_image_to_numpy(dummy_skia_image):
    """Tests the to_numpy() conversion method."""
    image = BitmapImage(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))

    numpy_bgra = image.to_numpy(mode='BGRA')
    assert numpy_bgra.shape == (2, 2, 4)
    assert np.array_equal(numpy_bgra[0, 0], [0, 0, 255, 255])
    numpy_rgba = image.to_numpy()
    assert numpy_rgba.shape == (2, 2, 4)
    assert np.array_equal(numpy_rgba[0, 0], [255, 0, 0, 255])
    numpy_rgb = image.to_numpy(mode='RGB')
    assert numpy_rgb.shape == (2, 2, 3)
    assert np.array_equal(numpy_rgb[0, 0], [255, 0, 0])
    numpy_grayscale = image.to_numpy(mode='Grayscale')
    assert numpy_grayscale.shape == (2, 2)
    assert np.array_equal(numpy_grayscale[0, 0], 76)

    with pytest.raises(ValueError):
        image.to_numpy(mode='invalid')

def test_image_to_bytes(dummy_skia_image):
    """Tests that to_bytes returns the expected raw bytes."""
    image = BitmapImage(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))

    expected_bytes = bytes([0, 0, 255, 255] * 4)
    assert image.to_bytes() == expected_bytes

def test_image_to_pillow(dummy_skia_image):
    """Tests conversion to a Pillow image."""
    from PIL import Image as PillowImage

    image = BitmapImage(skia_image=dummy_skia_image, content_box=Box(0, 0, 0, 0))
    pillow_image = image.to_pillow()

    assert isinstance(pillow_image, PillowImage.Image)
    assert pillow_image.size == (2, 2)
    assert pillow_image.mode == "RGBA"
    assert pillow_image.getpixel((0, 0)) == (255, 0, 0, 255)

def test_to_bytes_format_consistency():
    """Tests that to_bytes() consistently returns BGRA unpremultiplied format.
    
    This test verifies the fix for cross-platform consistency issues where
    the byte format could differ between OS (Windows vs Linux/macOS).
    The fix ensures to_bytes() always returns BGRA with unpremultiplied alpha.
    """
    from pictex import Canvas, Text, SolidColor
    
    # SolidColor(255, 0, 0, 128) = 50% transparent red
    canvas = Canvas().size(2, 2).background_color(SolidColor(255, 0, 0, 128))
    image = canvas.render(Text(""))
    raw_bytes = image.to_bytes()
    
    # Verify the total byte length (2x2 pixels * 4 bytes per pixel)
    assert len(raw_bytes) == 16
    
    byte_array = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((2, 2, 4))
    
    # All pixels should be identical (solid red background at 50% opacity)
    # BGRA format: [B=0, G=0, R=255, A=128]
    first_pixel = byte_array[0, 0]
    
    assert first_pixel[0] == 0    # B
    assert first_pixel[1] == 0    # G
    assert first_pixel[2] == 255  # R
    assert first_pixel[3] == 128  # A
    
    # All pixels should be identical (uniform background)
    for i in range(2):
        for j in range(2):
            assert np.array_equal(byte_array[i, j], first_pixel), \
                f"Pixel ({i},{j}) differs from expected: {byte_array[i, j]} != {first_pixel}"
    
    # Test to_numpy() BGRA mode - should match to_bytes()
    numpy_bgra = image.to_numpy('BGRA')
    assert numpy_bgra.shape == (2, 2, 4)
    assert np.array_equal(numpy_bgra, byte_array), \
        "to_numpy('BGRA') should return the same data as to_bytes()"
    
    # Verify BGRA unpremultiplied values
    assert numpy_bgra[0, 0][0] == 0    # B
    assert numpy_bgra[0, 0][1] == 0    # G
    assert numpy_bgra[0, 0][2] == 255  # R (unpremultiplied - should be 255, not 128)
    assert numpy_bgra[0, 0][3] == 128  # A
    
    # Test to_numpy() RGBA mode - should have channels swapped
    numpy_rgba = image.to_numpy('RGBA')
    assert numpy_rgba.shape == (2, 2, 4)
    
    # Verify RGBA unpremultiplied values (R and B swapped from BGRA)
    assert numpy_rgba[0, 0][0] == 255  # R (unpremultiplied)
    assert numpy_rgba[0, 0][1] == 0    # G
    assert numpy_rgba[0, 0][2] == 0    # B
    assert numpy_rgba[0, 0][3] == 128  # A
    
    # Test to_pillow() - should return correct RGBA unpremultiplied values
    pillow_image = image.to_pillow()
    assert pillow_image.mode == 'RGBA'
    assert pillow_image.size == (2, 2)
    
    # Verify all pixels in pillow image
    for i in range(2):
        for j in range(2):
            assert pillow_image.getpixel((j, i)) == (255, 0, 0, 128), \
                f"Pillow pixel ({j},{i}) should be (255, 0, 0, 128) unpremultiplied"

def test_image_with_render_tree(dummy_skia_image):
    """Tests BitmapImage with render tree functionality."""
    content_box = Box(x=10, y=20, width=30, height=40)
    
    # Create a mock render tree
    child_node = RenderNode(
        bounds=Box(x=5, y=5, width=10, height=10),
        children=[],
        node_type=NodeType.TEXT
    )
    root_node = RenderNode(
        bounds=Box(x=0, y=0, width=100, height=50),
        children=[child_node],
        node_type=NodeType.ROW
    )
    
    image = BitmapImage(skia_image=dummy_skia_image, content_box=content_box, render_tree=root_node)
    
    assert image.render_tree is root_node
    assert image.render_tree.node_type == NodeType.ROW
    assert len(image.render_tree.children) == 1
    assert image.render_tree.children[0].node_type == NodeType.TEXT
    
    # Test find_nodes_by_type
    text_nodes = image.render_tree.find_nodes_by_type(NodeType.TEXT)
    assert len(text_nodes) == 1
    assert text_nodes[0].bounds == Box(x=5, y=5, width=10, height=10)
    
    # Test visit_children
    visited_nodes = []
    def visitor(node):
        visited_nodes.append(node)
    
    image.render_tree.visit_children(visitor)
    assert len(visited_nodes) == 1
    assert visited_nodes[0].node_type == NodeType.TEXT
