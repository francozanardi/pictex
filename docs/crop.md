## Smart Sizing and Cropping

By default, `PicTex` automatically calculates the smallest possible canvas size to fit your text and all its effects (like shadows). Sometimes, you may want more control. The `render()` method accepts a `crop_mode` argument:

-   `CropMode.NONE` (Default): The canvas will be large enough to include all effects, including the full extent of shadows.
-   `CropMode.CONTENT_BOX`: The canvas will be cropped to the "content box" (the text area plus its padding). This is useful if you want to ignore shadows for layout purposes.
-   `CropMode.SMART`: A smart crop that trims all fully transparent pixels from the edges of the image. This is often the best choice for the tightest possible output.

```python
from pictex import Canvas, CropMode

canvas = Canvas().font_size(100).add_shadow(offset=(10,10), blur_radius=20, color="white")
canvas.background_color("blue")

# Render with different crop modes
img_none = canvas.render("Test", crop_mode=CropMode.NONE)
img_smart = canvas.render("Test", crop_mode=CropMode.SMART)
img_content_box = canvas.render("Test", crop_mode=CropMode.CONTENT_BOX)

# We save them as JPG images to force a black background instead of transparent, so it's easier to see the difference
img_none.save("test_none.jpg")
img_smart.save("test_smart.jpg")
img_content_box.save("test_content_box.jpg")
```

**`CropMode.NONE`** (default):

![None crop result](assets/crop-1-none.jpg)

**`CropMode.SMART`**:

![Smart crop result](assets/crop-1-smart.jpg)

**`CropMode.CONTENT_BOX`**:

![Content-box crop result](assets/crop-1-cb.jpg)
