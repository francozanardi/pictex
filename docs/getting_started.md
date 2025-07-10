# Getting Started & Core Concepts

Welcome to the `PicTex` documentation! This guide will walk you through the core concepts of the library.

## The Core Idea: Canvas and Image

The two most important classes in `pictex` are `Canvas` and `Image`.

1.  **`Canvas`**: Think of a `Canvas` as a **reusable style template**. You use its fluent methods (`.font_size()`, `.color()`, etc.) to build up a set of styling rules. You create a `Canvas` once and can use it many times.

2.  **`Image`**: An `Image` is the **final rendered product**. You get an `Image` object by calling `canvas.render("some text")`. This object holds the pixel data and provides helpful methods to save, display, or convert it.

This separation allows for clean and efficient code:

```python
# Create one style template
my_template = Canvas().font_size(80).color("blue")

# Render multiple images from the same template
image1 = my_template.render("First Text")
image2 = my_template.render("Second Text")

image1.save("first.png")
image2.save("second.png")
```

## Smart Sizing and Cropping

By default, `pictex` automatically calculates the smallest possible canvas size to fit your text and all its effects (like shadows). Sometimes, you may want more control. The `render()` method accepts a `crop_mode` argument:

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

![None crop result](assets/getting-started-1-none.jpg)

**`CropMode.SMART`**:

![Smart crop result](assets/getting-started-1-smart.jpg)

**`CropMode.CONTENT_BOX`**:

![Content-box crop result](assets/getting-started-1-cb.jpg)

## Working with the `Image` Object

```python
image = canvas.render("Hello")

# Save to a file
image.save("hello.png")

# Get a Pillow Image object (requires `pip install Pillow`)
pil_image = image.to_pillow()
pil_image.show()

# Get a NumPy array for use with OpenCV or other libraries
# Default is BGRA format for OpenCV
numpy_array_bgra = image.to_numpy()
# Get in RGBA format for Matplotlib, etc.
numpy_array_rgba = image.to_numpy(rgba=True)
```

Now that you understand the basics, dive into the specific styling guides to see everything `pictex` can do!
