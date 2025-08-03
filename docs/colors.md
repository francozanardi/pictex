# Styling Guide: Colors & Gradients

Anywhere a `color` is required, you can use a **Solid Color** or a **Gradient**.

## Solid Colors

They can be specified using the `SolidColor` class or using a string in different formats:

| Format           | Example         | Description                               |
| ---------------- | --------------- | ----------------------------------------- |
| Named Color      | `"red"`, `"gold"` | Common CSS color names.                   |
| 6-digit Hex      | `"#FF5733"`     | Standard RRGGBB format.                   |
| 3-digit Hex      | `"#F53"`         | Shorthand for `"#FF5533"`.                |
| 8-digit Hex (HexA) | `"#FF573380"`   | RRGGBBAA, where AA is the alpha/opacity. |

For example, all these are valid ways to set the color to red:

```python
from pictex import Canvas, SolidColor

Canvas().color("#FF0000FF")
Canvas().color("#FF0000")
Canvas().color("#F00")
Canvas().color("red")
Canvas().color(SolidColor(255, 0, 0, 255))
Canvas().color(SolidColor(255, 0, 0))
```

## Linear Gradients

**You can use a `LinearGradient` object anywhere a color is accepted**: in `.color()`, `.text_stroke()`, `border()`, `.background_color()`, and even in text decorations like `.underline()`. Only shadow colors must be solid.

A `LinearGradient` has a few key parameters:
-   `colors`: A list of color strings.
-   `stops` (Optional): A list of floats (0.0 to 1.0) specifying the position of each color.
-   `start_point` & `end_point` (Optional): Define the direction of the gradient. `(0,0)` is top-left, `(1,1)` is bottom-right.

### Example: Gradient on a Background

```python
from pictex import Canvas, LinearGradient

gradient = LinearGradient(
    colors=["#43C6AC", "#191654"],
    start_point=(0.0, 0.0), # Top-left
    end_point=(1.0, 1.0)   # Bottom-right
)

canvas = (
    Canvas()
    .font_size(90)
    .color("white")
    .padding(40)
    .background_color(gradient)
    .border_radius(25)
)

canvas.render("Gradient BG").save("gradient_bg.png")
```

![Background gradient result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754099560/gradient_bg_d3ivme.png)

### Showcase: Gradients Everywhere

Let's combine everything. Here, we apply different gradients to the text fill, its outline, and its underline.

```python
from pictex import Canvas, LinearGradient

text_gradient = LinearGradient(colors=["#FFD700", "#FF6B6B"])
stroke_gradient = LinearGradient(colors=["#4A00E0", "#8E2DE2"])
underline_gradient = LinearGradient(
    colors=["#00F260", "#0575E6"],
    start_point=(0.5, 0.0),
    end_point=(0.5, 1.0)
)
border_gradient = LinearGradient(colors=["blue", "cyan"])

canvas = (
    Canvas()
    .font_family("Impact")
    .font_size(150)
    .color(text_gradient)
    .text_stroke(width=10, color=stroke_gradient)
    .underline(thickness=15, color=underline_gradient)
    .border(width=5, color=border_gradient)
)

canvas.render("GRADIENTS!").save("gradients_everywhere.png")
```

![Gradients everywhere result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754099560/gradients_everywhere_rlk3qo.png)
