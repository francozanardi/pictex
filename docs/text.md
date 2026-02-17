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
1.  Your primary font set with `.font_family()`, or the bundled **Inter Variable** font if none is specified.
2.  Any custom fallback fonts you provide with `.font_fallbacks()`.
3.  Automatic system font discovery: PicTex automatically find a system font that supports the grapheme being rendered.

If a provided font is not found, a warning message is displayed and the font is ignored.

> **Note**: PicTex includes Inter Variable as a bundled default font. This ensures consistent rendering across all platforms, including environments like Google Colab where system fonts may be unavailable.

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

![Font fallback result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102756/font_fallback_example_bhrkg1.png)

## Variable Fonts

`PicTex` has support for **Variable Fonts**. If you provide a variable font file, it will automatically apply the `weight` and `style` settings to the font's variation axes (`wght`, `ital`, `slnt`).

```python
from pictex import Canvas, FontWeight, FontStyle

# Using a variable font file and setting its axes
canvas = (
    Canvas()
    .font_family("Oswald-VariableFont_wght.ttf")
    .font_size(80)
    .font_weight(FontWeight.BLACK) # Sets 'wght' axis to 900
    .color("orange")
)

canvas.render("Variable Font").save("variable_font.png")
```

![Variable font result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102764/variable_font_skmjc6.png)

`FontWeight` can be an enum member (e.g., `FontWeight.BOLD`) or an integer from 100 to 900.

## Text Shaping

`PicTex` includes advanced text shaping capabilities that improve text rendering quality through kerning, ligatures, and complex script support. This feature is automatically enabled and works behind the scenes to provide professional typography.

### Kerning

Kerning automatically adjusts the spacing between specific character pairs for better visual balance. For example, characters like "AV", "TY", or "Wo" will have optimized spacing.

### Ligatures

When using fonts that support ligatures, character sequences are automatically replaced with single, specially designed glyphs for improved readability.

```python
from pictex import Canvas, NamedColor

(
    Canvas()
    .font_family("FiraCode-Medium.ttf")
    .font_size(100)
    .background_color(NamedColor.BEIGE)
    .color(NamedColor.BLUE)
    .render("-> != <= ==")
    .save("ligature.png")
)
```

![Ligature result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1759127040/docs-ligature_rwlxmg.png)

### Complex Script Support

Text shaping properly handles complex scripts like Arabic, where characters need to connect and change forms based on their position.

```python
from pictex import Canvas, NamedColor

(
    Canvas()
    .font_size(100)
    .background_color(NamedColor.BEIGE)
    .color(NamedColor.DARKGREEN)
    .render("كتاب")
    .save("docs-arabic.png")
)
```

![Script support result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1759127040/docs-arabic_yffazq.png)

### Complex Emoji Sequences

Multi-part emoji sequences (like 👩‍🔬) are rendered as single glyphs instead of separate emoji characters.

```python
from pictex import Canvas

(
    Canvas()
    .font_size(100)
    .render("👩‍🔬 🏳️‍🌈")
    .save("docs-emoji.png")
)
```

![Emoji sequences result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1759127041/docs-emoji_ekahio.png)

## Multi-line Text and Alignment

`PicTex` fully supports multi-line text using newline characters (`\n`). Additionally, text can automatically wrap when placed in containers with fixed widths.

-   `.text_align()`: Controls how text lines are aligned within the text block. Accepts `TextAlign.LEFT`, `TextAlign.CENTER`, or `TextAlign.RIGHT`. If not set, it defaults to `LEFT` in LTR contexts and `RIGHT` in RTL contexts.
-   `.line_height()`: Sets the spacing between lines as a multiplier of the font size. A value of `1.5` means 150% spacing.
-   `.text_wrap()`: Controls whether text automatically wraps to fit container width. Accepts `"normal"` (default, wrapping enabled) or `"nowrap"` (wrapping disabled).

```python
from pictex import Canvas, TextAlign

canvas = (
    Canvas()
    .font_family("Times New Roman")
    .font_weight(700)
    .font_size(50)
    .color("magenta")
    .text_align(TextAlign.CENTER)  # a string is also accepted ("center")
    .line_height(1.2)
    .padding(20)
)

text = "This is an example of centered,\nmulti-line text\nwith custom line spacing."
canvas.render(text).save("alignment_example.png")
```

![Multiline result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102754/alignment_example_dnk5t4.png)

## Text Direction (LTR / RTL)

PicTex automatically applies the **Unicode Bidirectional Algorithm (BiDi)** to all text, ensuring proper visual ordering of mixed-direction content without any configuration required. It also replicates CSS-compliant layout behavior for RTL contexts.

-   **Automatic BiDi Processing**: The BiDi algorithm runs automatically on every text element, properly reordering characters in mixed scripts (e.g., English + Arabic). This includes correct positioning of punctuation: in RTL, `"Hello!"` visually becomes `"!Hello"`.
-   **Manual Direction Override**: Use `.direction("rtl")` or `.direction("ltr")` to set an explicit base paragraph direction.
-   **Automatic Alignment Resolution**: In an RTL context, `text_align()` automatically defaults to `TextAlign.RIGHT` if not explicitly set, ensuring text aligns correctly with the paragraph flow.
-   **Layout Mirroring**: `Row` containers automatically reverse the visual order of their children when `direction("rtl")` is applied, mirroring the behavior of `direction: rtl` in CSS Flexbox.
-   **Direction Inheritance**: The direction property is inherited by all children within a container.

```python
from pictex import Canvas, Row, Column, Text

# Automatic BiDi - no direction needed
# Arabic text is automatically reversed
Canvas().render("Hello مرحبا World").save("auto_bidi.png")

# RTL base direction - affects alignment and layout
container = (
    Column(
        # This Row will be mirrored: [B] [A]
        Row(
            Text("A").background_color("red").padding(5),
            Text("B").background_color("blue").padding(5),
        ).gap(10),

        # This text will be right-aligned automatically
        Text("Right-aligned text").size(width=400), 
        
        # Explicit override to LTR
        Text("LTR Override").direction("ltr"), 
    )
    .direction("rtl")
    .padding(20)
    .gap(20)
)

Canvas().render(container).save("direction_example.png")
```

### Text Wrapping

When text is placed inside containers with fixed widths, it can automatically wrap to multiple lines:

```python
from pictex import Canvas, Text, Column

canvas = Canvas().font_family("Arial").font_size(16)

# Text will automatically wrap to fit the 200px width
long_text = "This is a very long sentence that will automatically wrap to multiple lines when placed inside a container with a fixed width."

wrapped_text = Text(long_text)
container = Column(wrapped_text).size(width=200).padding(10)

canvas.render(container).save("text_wrapping_example.png")
```

You can also disable text wrapping:

```python
# This text will not wrap and may overflow the container
no_wrap_text = Text(long_text).text_wrap("nowrap")
container = Column(no_wrap_text).size(width=200).padding(10)
```

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

![Underline result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102761/underline_lqz7fy.png)


![Strikethrough result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102759/strikethrough_jaofgg.png)

## Text Shadows

Applies one or more shadows directly to the text glyphs. To add multiple shadows, pass multiple `Shadow` objects. This method is declarative and will override any previous text shadows.

A `Shadow` instance has:
-   `offset`: A tuple `(x, y)` for the shadow's position.
-   `blur_radius`: The amount of blur to apply.
-   `color`: The color of the shadow.

```python
from pictex import Canvas, Text, Shadow

canvas =(
    Canvas()
    .font_size(120)
    .font_family("Impact")
    .color("#00FFAA")
    .text_shadows(
        Shadow(offset=(0, 0), blur_radius=2, color="#00FFAA"),
        Shadow(offset=(0, 0), blur_radius=5, color="#FFFFFF")
    )
)
canvas.render("NEON").save("neon.png")
```

![Text shadows result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754102759/neon_w7hnrf.png)

## Outline Stroke

The `.text_stroke()` method adds a stroke around the text.

By default, it follows CSS standards where the stroke is centered on the text path (half inside, half outside). You can control the stroke rendering with the `mode` parameter:

-   `"center"` (default): CSS-compliant centered stroke
-   `"outline"`: Stroke only outside the text (prevents thinning at large widths)
-   `"inline"`: Stroke only inside the text

```python
from pictex import Canvas

# Default CSS-compliant stroke
canvas = (
    Canvas()
    .font_size(150)
    .font_family("Impact")
    .background_color("beige")
    .color("yellow")
    .text_stroke(width=7, color="black")
)

canvas.render("COMIC").save("comic_style.png")
```

![Outline stroke result](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1759089537/comic_style_pqgvq3.png)
