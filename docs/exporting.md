# Exporting Your Image

Once you have built your visual composition, PicTex provides flexible options for exporting it to both raster (pixel-based) and vector (path-based) formats.

## Exporting to Raster Images (.png, .jpg)

To generate a raster image, use the `.render()` method. This returns a `BitmapImage` object, which holds the pixel data and provides helpful methods to save, display, or convert it.

```python
from pictex import Canvas

canvas = Canvas().font_size(80).color("blue")
image = canvas.render("Hello, World!")

# Save to a file (format is inferred from extension)
image.save("output.png")
image.save("output.jpg", quality=90)
```

### Controlling Raster Size with `crop_mode`

The `.render()` method accepts a `crop_mode` argument to give you full control over the final image dimensions.

-   `CropMode.NONE` (Default): The canvas will be large enough to include all effects, including the full extent of shadows.
-   `CropMode.CONTENT_BOX`: The canvas will be cropped to the "content box" of the root element. This is useful if you want to ignore shadows for layout purposes.
-   `CropMode.SMART`: A smart crop that trims all fully transparent pixels from the edges of the image. This is often the best choice for the tightest possible output.

```python
from pictex import Canvas, CropMode

canvas = Canvas().font_size(100).add_shadow(offset=(10,10), blur_radius=20, color="white")
canvas.background_color("blue")

# Render with different exporting modes
img_none = canvas.render("Test", crop_mode=CropMode.NONE)
img_smart = canvas.render("Test", crop_mode=CropMode.SMART)
img_content_box = canvas.render("Test", crop_mode=CropMode.CONTENT_BOX)

# We save them as JPG images to force a black background instead of transparent, so it's easier to see the difference
img_none.save("test_none.jpg")
img_smart.save("test_smart.jpg")
img_content_box.save("test_content_box.jpg")
```

**`CropMode.NONE`** (default):

![None crop result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754099896/test_none_qayqye.jpg)

**`CropMode.SMART`**:

![Smart crop result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754099896/test_smart_c8vl7j.jpg)

**`CropMode.CONTENT_BOX`**:

![Content-box crop result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754099895/test_content_box_eecjyp.jpg)

### Converting to Other Formats

The `Image` object can be easily converted for use with other popular libraries.
```python
# Get a Pillow Image object (requires `pip install Pillow`)
pil_image = image.to_pillow()

# Get a NumPy array for use with OpenCV (BGRA format) or Matplotlib (RGBA).
numpy_array = image.to_numpy(mode="RGBA")
```

## Exporting to Vector Images (.svg)

To generate an SVG, use the `.render_as_svg()` method. This returns a `VectorImage` object.

```python
vector_image = canvas.render_as_svg("Hello, SVG!")
vector_image.save("output.svg")
```

> Note: Shadows are not supported yet in SVG

### Understanding Font Handling in SVG

Handling fonts is the most critical aspect of creating portable SVGs. `PicTex` gives you precise control over this via the `embed_font` parameter in the `render_as_svg()` method.

The behavior changes depending on whether you are using a **font file** (e.g., from a `.ttf` path) or a **system font** (e.g., `"Arial"`).

### Scenario 1: Using a Font File (e.g., `.font_family("path/to/font.ttf")`)

This is the recommended approach for achieving consistent visual results.

#### `embed_font=True` (default)
-   **What it does:** The entire font file is encoded in Base64 and embedded directly within the SVG file using a `@font-face` rule.
-   **Result:** The SVG is **fully self-contained and portable**. It will render identically on any device, regardless of a user's installed fonts.
-   **Trade-off:** The file size of the SVG will increase by roughly 133% of the original font file's size.

```python
# This creates a completely portable SVG
vector_image = canvas.render_as_svg("Portable & Perfect", embed_font=True)
vector_image.save("portable_text.svg")
```

#### `embed_font=False`
-   **What it does:** The SVG will still contain a `@font-face` rule, but instead of embedding the font data, it will reference the font file using a relative path (e.g., `src: url('path/to/font.ttf')`).
-   **Result:** The SVG file itself is very small. However, for it to render correctly, the font file **must be distributed alongside the SVG** and kept in the same relative path. This is useful for web projects where you manage fonts and SVGs as separate assets.
-   **Trade-off:** The SVG is no longer self-contained.

```python
# This creates a lightweight SVG that depends on an external font file
vector_image = canvas.render_as_svg("Linked Font", embed_font=False)
vector_image.save("linked_text.svg")
# You must also provide the font file for "linked_text.svg" to work correctly.
```

### Scenario 2: Using a System Font (e.g., `.font_family("Arial")`)

This applies when you specify a font by name or when `PicTex` uses a system font as a fallback (e.g., for an emoji).

-   **What it does:** In this case, the `embed_font` parameter has **no effect**, as `PicTex` does not have access to the font's file path to be able to read and embed it.
-   **Result:** The SVG will always reference the font by its family name (e.g., `font-family: 'Arial'`). The rendering completely relies on the viewing system having that specific font installed. If the font is not found, the viewer will substitute it with a default, which may alter the appearance.
-   **Warning:** If you use `embed_font=True` with a system font, `PicTex` will issue a warning to inform you that the font could not be embedded.

### Summary of Font Handling

| Font Source          | `embed_font=True` (Default)                                   | `embed_font=False`                                         |
| -------------------- | ------------------------------------------------------------- | ---------------------------------------------------------- |
| **Font from File**   | **Fully Portable SVG.** Font is embedded (Base64).            | **Linked SVG.** Relies on external font file at a relative path. |
| **System Font**      | **System-Dependent SVG.** Font is referenced by name. (Warning issued) | **System-Dependent SVG.** Font is referenced by name.      |
