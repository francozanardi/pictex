# Getting Started & Core Concepts

Welcome to the `PicTex` documentation! This guide will walk you through the core concepts of the library.

## The Core Idea: Canvas and Image

The two most important classes in `PicTex` are `Canvas` and `Image`.

1.  **`Canvas`**: Think of a `Canvas` as a **reusable style template**. You use its fluent methods (`.font_size()`, `.color()`, etc.) to build up a set of styling rules. You create a `Canvas` once and can use it many times.

2.  **`Image`**: An `Image` is the **final rendered product** when you use `Canvas.render(...)`. This object holds the pixel data and provides helpful methods to save, display, or convert it.

3.  **`VectorImage`**: This is a **vector image** containing SVG data, returned by `Canvas.render_as_svg(...)`.

This separation allows for clean and efficient code:

```python
# Create one style template
my_template = Canvas().font_size(80).color("blue")

# Render multiple images from the same template
raster_image = my_template.render("First Text")
vector_image = my_template.render_as_svg("Second Text")

raster_image.save("first.png")
vector_image.save("second.svg")
```

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

## Working with the `VectorImage` Object

The `VectorImage` object is simple. It holds the SVG content as a string.

```python
vector_image = canvas.render_as_svg("Hello SVG")

# Save to a file
vector_image.save("hello.svg")

# Get the raw SVG string
svg_string = vector_image.svg
print(svg_string)
```

## What's Next?

You now understand the basic workflow of `PicTex`. The real power of the library lies in its rich styling capabilities. We recommend you explore the guides in the following order:

1.  **[Text & Fonts](./text.md)**
    *Learn how to use custom fonts, variable fonts, set weights and styles, and master the automatic font fallback system for emojis and special characters.*

2.  **[Colors & Gradients](./colors.md)**
    *Discover how to use solid colors and apply beautiful linear gradients to text, backgrounds, and even decorations.*

3.  **[Containers & Effects](./effects.md)**
    *Dive into creating backgrounds, padding, outlines, and adding depth with multiple text and box shadows.*

4.  **[Smart Sizing & Cropping](./crop.md)**
    *Take full control over the final image dimensions with different cropping strategies.*

5.  **[Exporting to SVG](./exporting_svg.md)**
    *Export your canvas as an SVG image.*