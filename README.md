# PicTex

[![PyPI version](https://badge.fury.io/py/pictex.svg?v=2)](https://pypi.org/project/pictex/)
[![CI Status](https://github.com/francozanardi/pictex/actions/workflows/test.yml/badge.svg)](https://github.com/francozanardi/pictex/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/francozanardi/pictex/branch/main/graph/badge.svg)](https://codecov.io/gh/francozanardi/pictex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library to create beautifully styled text images with a simple, fluent API. Powered by Skia.

![PicTex](https://raw.githubusercontent.com/francozanardi/pictex/main/docs/assets/readme-1.png)

**`PicTex`** makes it easy to generate styled text images for social media, video overlays, digital art, or any application where stylized text is needed. It abstracts away the complexity of graphics libraries, offering a declarative and chainable interface inspired by CSS.

## Features

-   **Fluent & Reusable API**: Build styles declaratively and reuse them.
-   **Rich Styling**: Gradients, multiple shadows, outlines, and text decorations.
-   **Advanced Typography**: Custom fonts, variable fonts, line height, and alignment.
-   **Automatic Font Fallback**: Seamlessly render emojis and special characters even if your main font doesn't support them.
-   **Flexible Output**: 
    -   **Raster**: Save as PNG/JPEG/WebP, or convert to NumPy/Pillow.
    -   **Vector**: Export to a clean, scalable SVG file with font embedding.
-   **High-Quality Rendering**: Powered by Google's Skia graphics engine.

## Installation

```bash
pip install pictex
```

## Quickstart

Creating a stylized text image is as simple as building a `Canvas` and calling `.render()`.

```python
from pictex import Canvas

# 1. Create a style template using the fluent API
canvas = (
    Canvas()
    .font_family("path/to/font.ttf")
    .font_size(60)
    .color("white")
    .padding(20)
    .background_color(LinearGradient(["#2C3E50", "#FD746C"]))
    .background_radius(10)
    .add_shadow(offset=(2, 2), blur_radius=3, color="black")
)

# 2. Render some text using the template
image = canvas.render("Hello, PicTex! 🎨✨")

# 3. Save or show the result
image.save("hello.png")

```

![Quickstart result](https://raw.githubusercontent.com/francozanardi/pictex/main/docs/assets/readme-2.png)

You can also render it as SVG using `Canvas.render_as_svg()`.
```
image = canvas.render_as_svg("Hello, PicTex! 🎨✨")
image.save("hello.svg")
```

![Quickstart SVG result](https://raw.githubusercontent.com/francozanardi/pictex/main/docs/assets/readme-3.svg)

## 📚 Dive Deeper

For a complete guide on all features, including text decorations, advanced gradients, smart cropping, and more, check out our full documentation:

-   [**Getting Started & Core Concepts**](docs/getting_started.md)
-   [**Exporting to SVG**](docs/exporting_svg.md)
-   [**Styling Guide: Colors & Gradients**](docs/colors.md)
-   [**Styling Guide: Text & Fonts**](docs/text.md)
-   [**Styling Guide: Containers & Effects**](docs/effects.md)
-   API Reference (coming soon)

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/francozanardi/pictex/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
