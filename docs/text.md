# Styling Guide: Text & Fonts

This guide covers all options related to fonts, typography, and text decorations.

## Font Family, Size, Weight, and Style

You can use system-installed fonts by name or provide a path to a `.ttf` or `.otf` file.

```python
from pictex import Canvas, FontWeight, FontStyle

# Using a system font
canvas_system = (
    Canvas()
    .font_family("Georgia")
    .font_size(80)
    .font_weight(FontWeight.BOLD)
    .font_style(FontStyle.ITALIC)
)

# Using a local font file
canvas_local = Canvas().font_family("assets/fonts/Inter-Variable.ttf").font_size(80)
```

## Font Fallbacks and Emoji Support

One of `PicTex`'s most powerful features is its automatic font fallback system. If your primary font doesn't support a specific character (like an emoji `✨` or a symbol `→`), `PicTex` will automatically search through a list of fallback fonts to find one that does.

This means you can render complex, multi-lingual text and emojis without worrying about missing characters (often shown as `□`).

### How It Works

The fallback chain is:
1.  Your primary font set with `.font_family()`.
2.  Any custom fallback fonts you provide with `.font_fallbacks()`.
3.  A list of default system emoji fonts (`Segoe UI Emoji` on Windows, `Apple Color Emoji` on macOS, `Noto Color Emoji` on Linux).

If a provided font is not found, a warning message is displayed and the font is ignored.

### Providing Custom Fallbacks

You can specify your own list of fallback fonts. This is useful if you are working with multiple languages and want to ensure a specific look.

```python
from pictex import Canvas

# A font that doesn't support Japanese or emojis
primary_font = "Lato-BoldItalic.ttf" 

# A Japanese font
japanese_font = "NotoSansJP-Regular.ttf"

canvas = (
    Canvas()
    .font_family(primary_font)
    .font_fallbacks(japanese_font)
    .font_size(80)
    .color("olive")
    .padding(20)
)

text = "Hello, 世界 ✨"
canvas.render(text).save("font_fallback_example.png")
```

![Font fallback result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831766/text-0_nxafcr.png)

## Variable Fonts

`PicTex` has support for **Variable Fonts**. If you provide a variable font file, it will automatically apply the `weight` and `style` settings to the font's variation axes (`wght`, `ital`, `slnt`).

```python
from pictex import Canvas, FontWeight, FontStyle

# Using a variable font file and setting its axes
canvas = (
    Canvas()
    .font_family("assets/Variable-Font.ttf")
    .font_size(80)
    .font_weight(FontWeight.BLACK) # Sets 'wght' axis to 900
    .font_style(FontStyle.ITALIC)  # Sets 'ital' axis to 1
    .color("orange")
)

canvas.render("Variable Font").save("variable_font.png")
```

![Variable font result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831766/text-1_grcdal.png)

`FontWeight` can be an enum member (e.g., `FontWeight.BOLD`) or an integer from 100 to 900.

## Multi-line Text and Alignment

`PicTex` fully supports multi-line text using newline characters (`\n`).

-   `.alignment()`: Controls how text lines are aligned within the text block. Accepts `Alignment.LEFT`, `Alignment.CENTER`, or `Alignment.RIGHT`.
-   `.line_height()`: Sets the spacing between lines as a multiplier of the font size. A value of `1.5` means 150% spacing.

```python
from pictex import Canvas, Alignment

canvas = (
    Canvas()
    .font_family("Times New Roman")
    .font_weight(700)
    .font_size(50)
    .color("magenta")
    .alignment(Alignment.CENTER) # a string is also accepted ("center")
    .line_height(1.2)
    .padding(20)
)

text = "This is an example of centered,\nmulti-line text\nwith custom line spacing."
canvas.render(text).save("alignment_example.png")
```

![Multiline result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831767/text-2_tvcdeh.png)

## Text Decorations

You can add `underline` and `strikethrough` decorations. As shown in the Gradients guide, the `color` for a decoration can also be a `LinearGradient`.

If the `color` is not defined, it will use the font color.

```python
from pictex import Canvas

# Simple underline
canvas1 = Canvas().font_size(80).color("blue").underline(10)
canvas1.render("Underlined").save("underline.png")

# Styled strikethrough
canvas2 = Canvas().font_size(80).color("blue").strikethrough(thickness=10, color="red")
canvas2.render("Strikethrough").save("strikethrough.png")
```

![Underline result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831766/text-3-u_fviyjk.png)


![Strikethrough result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1753831766/text-3-s_kkvrl8.png)
