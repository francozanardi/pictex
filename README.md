# Pictex

A powerful Python library to generate beautifully styled text images, powered by Skia.
It supports high-quality text rendering including custom fonts, shadows, strokes, and more.

## Installation

```bash
pip install pictex
```

## Usage

```python
from pictex import Canvas

# The canvas is where the texts will be rendered, it holds the styles to be used
canvas = (
    Canvas()
    .font_family("Roboto")
    .font_size(96)
    .color("#3498db")
    .shadow(offset=(5, 5), blur_radius=4, color="#2980b9")
)

# Here we save a image with the text "Hello, world!"
image = canvas.render("Hello, world!")
image.save("output.png")

# Here we create and save another image with the same styles and the text "Another text"
canvas.render("Another text").save("another.png") 
```
