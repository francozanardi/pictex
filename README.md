# PicTex

[![PyPI version](https://badge.fury.io/py/pictex.svg?v=4)](https://pypi.org/project/pictex/)
[![CI Status](https://github.com/francozanardi/pictex/actions/workflows/test.yml/badge.svg)](https://github.com/francozanardi/pictex/actions/workflows/test.yml)
[![Codecov](https://codecov.io/gh/francozanardi/pictex/branch/main/graph/badge.svg)](https://codecov.io/gh/francozanardi/pictex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library for creating complex visual compositions and beautifully styled images. Powered by Skia.

![PicTex](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831765/readme-1_vqnohh.png)

**`PicTex`** is a component-based graphics library that makes it easy to generate dynamic images for social media, video overlays, and digital art. It abstracts away the complexity of graphics engines, offering a declarative and chainable interface inspired by modern layout systems.

## Features

-   **Component-Based Layout**: Compose complex visuals by nesting powerful layout primitives like `Row`, `Column`, and `Image`.
-   **Rich Styling**: Gradients, multiple shadows, borders with rounded corners, and text decorations.
-   **Advanced Typography**: Custom fonts, variable fonts, line height, and alignment.
-   **Automatic Font Fallback**: Seamlessly render emojis and multilingual text.
-   **Flexible Output**: 
    -   **Raster**: Save as PNG/JPEG/WebP, or convert to NumPy/Pillow.
    -   **Vector**: Export to a clean, scalable SVG file with font embedding.
-   **High-Quality Rendering**: Powered by Google's Skia graphics engine.

## Installation

```bash
pip install pictex
```

## Quickstart

### Styled text image

Creating a stylized text image is as simple as building a `Canvas` and calling `.render()`.

```python
from pictex import Canvas, Shadow, LinearGradient

# 1. Create a style template using the fluent API
canvas = (
    Canvas()
    .font_family("Poppins-Bold.ttf")
    .font_size(60)
    .color("white")
    .padding(20)
    .background_color(LinearGradient(["#2C3E50", "#FD746C"]))
    .border_radius(10)
    .text_shadows(Shadow(offset=(2, 2), blur_radius=3, color="black"))
)

# 2. Render some text using the template
image = canvas.render("Hello, World! 🎨✨")

# 3. Save or show the result
image.save("hello.png")
```

![Quickstart result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754103059/hello_zqkkba.png)

### Composed elements

Compose elements like `Row`, `Column`, and `Text` to build complex visuals. PicTex's fluent API makes styling declarative and intuitive.

```python
from pictex import *

# 1. Build your visual components
avatar = (
    Image("avatar.png")
    .border_radius("50%")
    .background_color("silver")
    .border(3, "white")
    .box_shadows(Shadow(offset=(2, 2), blur_radius=5, color="black"))
)

user_info = Column(
    Text("Alex Doe").font_size(24).font_weight(700).color("#184e77"),
    Text("Graphic Designer").color("#edf6f9").text_shadows(Shadow(offset=(1, 1), blur_radius=1, color="black")),
).horizontal_align("center").gap(4)

# 2. Compose them in a layout container
card = (
    Column(avatar, user_info)
    .background_color(LinearGradient(["#d9ed92", "#52b69a"]))
    .border_radius(20)
    .padding(30)
    .horizontal_align("center")
    .gap(20)
)

# 3. Render and save the final image
canvas = Canvas().font_family("NataSans.ttf")
image = canvas.render(card)
image.save("profile_card.png")
```

![Quickstart result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754103067/profile_card_b7ofk7.png)

## More Examples

PicTex 1.0's layout engine unlocks a huge range of possibilities, from social media graphics to data visualizations. We've created a collection of ready-to-run examples to showcase what you can build.

| Preview                                                      | Description                                                                                                                                                                                                                    |
|:-------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![Tweet to Image Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754446864/tweet_ouzwyf.png)   | **Tweet to Image** <br/> Recreate the look and feel of a tweet, perfect for sharing on other social platforms. <br/> **[View Code »](https://github.com/francozanardi/pictex/blob/main/examples/tweet_card/tweet_card.py)**    |
| ![Data Table Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754446872/table_t8hoyi.png)            | **Data Table** <br/> Generate a clean, styled table from a 2D list. Includes headers, zebra-striping, and shadows. <br/> **[View Code »](https://github.com/francozanardi/pictex/blob/main/examples/table/table.py)**          |
| ![Code Snippet Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754446867/result_exfjqr.png) | **Code Snippet** <br/> Create beautifully syntax-highlighted images of your code snippets for tutorials or social media. <br/> **[View Code »](https://github.com/francozanardi/pictex/blob/main/examples/code_to_image/code_to_image.py)** |

Check out the full [examples](https://github.com/francozanardi/pictex/tree/main/examples) directory for more!

## 📚 Dive Deeper

For a complete guide on all features, from layout and the box model to advanced styling, check out our full documentation:

-   [**Getting Started**](https://pictex.readthedocs.io/en/latest/getting_started/)
-   [**Core Concepts**](https://pictex.readthedocs.io/en/latest/core_concepts/)
-   [**Styling Guide: The Box Model**](https://pictex.readthedocs.io/en/latest/box_model/)
-   [**Styling Guide: Colors & Gradients**](https://pictex.readthedocs.io/en/latest/colors/)
-   [**Styling Guide: Text & Fonts**](https://pictex.readthedocs.io/en/latest/text/)

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/francozanardi/pictex/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/francozanardi/pictex/LICENSE) file for details.
