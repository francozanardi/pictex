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
