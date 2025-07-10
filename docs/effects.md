# Styling Guide: Containers & Effects

This guide covers backgrounds, padding, shadows, and outlines.

## The Container: Background & Padding

The container is the box model around your text.

-   `.padding()`: Sets the space between the text and the edge of the background. Accepts 1, 2, or 4 values, just like in CSS.
-   `.background_color()`: Sets the background fill (can be a color or gradient).
-   `.background_radius()`: Creates rounded corners for the background.

## Shadows: `add_shadow` and `add_box_shadow`

`pictex` supports two types of shadows, and you can add multiple of each to create complex, layered effects.

1.  **Text Shadow (`.add_shadow()`)**: A shadow applied directly to the text glyphs.
2.  **Box Shadow (`.add_box_shadow()`)**: A shadow applied to the background container.

### Text Shadow (`.add_shadow()`)

You can add multiple shadows to create complex effects. The method is chainable.

-   `offset`: A tuple `(x, y)` for the shadow's position.
-   `blur_radius`: The amount of blur to apply.
-   `color`: The color of the shadow.

```python
from pictex import Canvas

canvas = (
    Canvas()
    .font_size(120)
    .font_family("Arial Black")
    .color("#FFFFFF")
    .add_shadow(offset=(3, 3), blur_radius=0, color="blue")
    .add_shadow(offset=(0, 0), blur_radius=10, color="#FFD700")
)

canvas.render("Layered").save("layered_shadow.png")
```

![Text shadow result](assets/effects-1.png)

### Box Shadow (`.add_box_shadow()`)

This applies a shadow to the background box, not the text itself. It shares the same parameters as `.add_shadow()`.

```python
from pictex import Canvas

canvas = (
    Canvas()
    .font_size(100)
    .padding(40)
    .background_color("white")
    .background_radius(20)
    .add_box_shadow(offset=(10, 10), blur_radius=3, color="black")
)

canvas.render("Floating").save("box_shadow.png")
```

![Box shadow result](assets/effects-2.png)

## Outline Stroke

The `.outline_stroke()` method adds a contour around the text. This is great for creating impactful, cartoon-style, or sticker-like text.

```python
from pictex import Canvas

canvas = (
    Canvas()
    .font_size(150)
    .font_family("Impact")
    .color("yellow")
    .outline_stroke(width=14, color="black")
)

canvas.render("COMIC").save("comic_style.png")
```

![Outline stroke result](assets/effects-3.png)
