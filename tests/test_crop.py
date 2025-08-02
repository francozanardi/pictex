from pictex import *
from .conftest import check_images_match

def test_render_with_smart_crop(file_regression):
    """Tests that the SMART exporting mode works correctly."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .text_shadows(Shadow((10, 10), 15, "#000")) # Large shadow to create extra space
    )
    image = canvas.render("SMART", crop_mode=CropMode.SMART)
    assert image.content_box.height < image.height
    assert image.content_box.width < image.width
    check_images_match(file_regression, image)

def test_render_with_content_box_crop(file_regression):
    """Tests that the CONTENT_BOX exporting mode works correctly."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(80)
        .background_color("blue")
        .text_shadows(Shadow((10, 10), 15, "#000"))
        .box_shadows(Shadow((10, 10), 15, "#000"))
    )
    image = canvas.render("CONTENT_BOX", crop_mode=CropMode.CONTENT_BOX)
    assert image.content_box.height == image.height
    assert image.content_box.width == image.width
    assert image.content_box.x == 0
    assert image.content_box.y == 0
    check_images_match(file_regression, image)
