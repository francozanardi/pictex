from pictex import VectorImage

def test_vector_image_properties():
    """Tests the basic properties and methods of the VectorImage class."""
    dummy_svg = '<svg width="10" height="10"><rect x="0" y="0" width="10" height="10" fill="red"/></svg>'
    vector_image = VectorImage(svg_content=dummy_svg)

    assert vector_image.svg == dummy_svg
    assert str(vector_image) == dummy_svg
    assert vector_image._repr_svg_() == dummy_svg
    assert isinstance(vector_image, VectorImage)
