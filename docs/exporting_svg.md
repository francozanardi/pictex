# Exporting to SVG

`PicTex` provides powerful support for exporting your styled text to a Scalable Vector Graphic (SVG) file. This is ideal for web applications, logos, and any use case where resolution-independent images are required.

## Basic Usage

To generate an SVG, simply use the `.render_as_svg()` method on your `Canvas`. This returns a `VectorImage` object.

```python
from pictex import Canvas

canvas = Canvas().font_size(100).color("purple")

vector_image = canvas.render_as_svg("Hello, SVG!")
vector_image.save("output.svg")
```

## Understanding Font Handling in SVG

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
