# Core Concepts: Builders & Layout

Welcome to PicTex's layout engine! With version 1.0, PicTex has evolved from a text-styler into a powerful visual composition tool. This guide introduces the core concepts of building and arranging elements.

## Everything is a Builder

In PicTex, every visual piece you create is a **Builder**. There are three main types:

1.  **Content Builders**: These are the basic building blocks that hold content.
    -   `Text()`: For displaying text.
    -   `Image()`: For displaying raster images.
2.  **Layout Builders**: These are containers that arrange other builders.
    -   `Row()`: Arranges its children horizontally.
    -   `Column()`: Arranges its children vertically.
3.  **Root Builder**:
    -   `Canvas()`: The top-level container that holds your entire composition and defines global styles.

You can nest these builders to create complex layouts. For example, a `Row` can contain a mix of `Image` and `Text` builders.

```python
from pictex import *

composition = Row(
    Column(
        Text("Col1").background_color("blue"),
        Text("Col1").background_color("red")
    ),
    Column(
        Text("Col2").background_color("blue"),
        Text("Col2").background_color("red")
    )
)
Canvas().render(composition).save("introduction.png")
```

![Introduction](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754098899/introduction_gtjc6f.png)

## Layout Builders: `Row` and `Column`

The real power of PicTex lies in how you can arrange elements inside `Row` and `Column` containers.

### Main Axis and Cross Axis

Every layout builder has two axes:
-   **Main Axis**: The direction in which children are placed. For `Row`, it's **horizontal**. For `Column`, it's **vertical**.
-   **Cross Axis**: The axis perpendicular to the main axis. For `Row`, it's **vertical**. For `Column`, it's **horizontal**.

### Distribution (Main Axis)

Distribution controls how children are spaced along the **main axis**, especially when the container is larger than the children combined.

-   **On a `Row`**: Use `.horizontal_distribution()`
-   **On a `Column`**: Use `.vertical_distribution()`

**Available Modes:**
-   `'left'` / `'top'` (Default): `[X|X|X|.........]`
-   `'center'`: `[.....|X|X|X|.....]`
-   `'right'` / `'bottom'`: `[.........|X|X|X]`
-   `'space-between'`: `[X|.....|X|.....|X]` (Space is only between elements)
-   `'space-around'`: `[..|X|.....|X|.....|X|..]` (Space around each element)
-   `'space-evenly'`: `[..|X|..|X|..|X|..]` (Space is equal everywhere)

```python
from pictex import *

def create_distribution_example(distribution):
    row_with_distribution = Row(
        Text("A").background_color("blue"),
        Text("B").background_color("red"),
        Text("C").background_color("green"),
    ).horizontal_distribution(distribution).border(4, "black").size(width=300)
    return Column(
        Text(distribution).font_size(40),
        row_with_distribution
    ).background_color("pink")

distributions = [
    "left",
    "center",
    "right",
    "space-between",
    "space-around",
    "space-evenly",
]
examples = []
for d in distributions:
    examples.append(create_distribution_example(d))


image = Canvas().font_size(80).render(Column(*examples).gap(20))
image.save("distribution.png")
```

![Distribution Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754098899/distribution_vr3al5.png)

### Alignment (Cross Axis)

Alignment controls how children are positioned along the **cross axis**.

-   **On a `Row`**: Use `.vertical_align()`
-   **On a `Column`**: Use `.horizontal_align()`

**Available Modes:**
-   `'top'` / `'left'` (Default): Aligns children to the start of the cross axis.
-   `'center'`: Centers children along the cross axis.
-   `'bottom'` / `'right'`: Aligns children to the end of the cross axis.
-   `'stretch'`: Resizes children to fill the container along the cross axis.

```python
from pictex import *

def create_alignment_example(align):
    row_with_alignment = Row(
        Text("A").background_color("blue").font_size(80),
        Text("B").background_color("red").font_size(65),
        Text("C").background_color("green").font_size(50),
    ).vertical_align(align).border(4, "black").gap(30)
    return Column(
        Text(align).font_size(40),
        row_with_alignment
    ).background_color("pink")

aligns = [
    "top",
    "center",
    "bottom",
    "stretch"
]
examples = []
for a in aligns:
    examples.append(create_alignment_example(a))

image = Canvas().font_size(80).render(Column(*examples).gap(20))
image.save("alignment.png")
```

![Alignment Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754774757/alignment_m66sum.png)

#### How `stretch` Works

The `'stretch'` alignment is particularly powerful. It makes all children in a container have the same height (in a `Row`) or width (in a `Column`), creating clean, uniform layouts.

**`stretch` only affects children whose size for that axis is set to `'auto'` (the default).**

If you give a child an explicit size (e.g., `.size(height=50)` or `.size(height='fit-content')`), that child will **opt out** of being stretched and will keep its specified size. This allows you to create flexible layouts with specific exceptions.

```python
from pictex import *

col = Column(
    Text("I will stretch").background_color("blue"),
    Text("I am fixed").background_color("green").size(width="fit-content"),
    Text("I will also stretch").background_color("red")
).horizontal_align('stretch')

Canvas().render(col).save("stretch.png")
```

![Stretch Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754774789/stretch_lxinzt.png)

### Spacing with `.gap()`

Instead of adding margins to each child, the cleanest way to add space between elements is with `.gap()`. This applies a consistent spacing on the **main axis**.

```python
# Add a 20px gap between all children in the column
card = Column(
    product_image,
    header,
    description
).gap(20)
```

### Breaking the Flow: `position()` and `absolute_position()`

Sometimes you need to place an element at a specific coordinate, ignoring the normal `Row` or `Column` flow. PicTex offers two powerful methods for this, each with a different frame of reference. When you use either method, the element is removed from the layout flow, and other elements will behave as if it isn't there.

#### Relative Positioning with `.position()`

This is the most common method for positioning. It places an element relative to its **direct parent's content area**. This means the `(0, 0)` origin is the corner *inside* the parent's padding and border. This is perfect for overlays within a component, like placing a badge on an image, because the positioned element will move along with its parent.

#### Absolute Positioning with `.absolute_position()`

This method provides an "escape hatch" from all parent containers. It places an element relative to the **root canvas**. The `(0, 0)` origin is the absolute top-left corner of the final rendered image, ignoring any margin, border, or padding on the root container itself. This is best for global elements like watermarks.

#### Visualizing the Difference

The following example makes the distinction clear. We create a `Canvas` with a large margin, border, and padding. Inside, we place two `Text` elements, both at `(0, 0)`—one with `absolute_position` and one with `position`.

```python
from pictex import Canvas, Text

(
    Canvas()
    .margin(25)
    .padding(25)
    .border(25, "red")
    .background_color("blue")
    .size(200, 200)
    .font_size(20)
    .color("orange")
    .render(
        Text("ABSOLUTE").absolute_position(0, 0),
        Text("RELATIVE").position(0, 0)
    )
).save("position.png")
```

![Positioning Example](https://res.cloudinary.com/dlvnbnb9v/image/upload/v1754260873/position_uxawu1.png)

As you can see:
-   **`ABSOLUTE`** is rendered at the true `(0, 0)` of the final image, ignoring the canvas's own box model.
-   **`RELATIVE`** is rendered at `(0, 0)` relative to the parent's **content area**. Its final position is correctly offset by the canvas's 25px margin, 25px border, and 25px padding.
