# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Inline Spans** (`Span`): Introduced a new `Span` builder for applying granular, rich formatting within a single text block.
  - Apply varied styles (color, font size/weight/style, decorations, gradients, stroke, shadows) to specific subsets of text.
  - Spans can be nested deeply; properties cascade down and inherit naturally unless explicitly overridden.
  - Fully compatible with automatic font fallbacks, complex emoji sequences, bidirectional text, and contextual character joining.

## [2.2.0] - 2026-03-29

### Added
- **Letter Spacing** (`letter_spacing()`): Controls the extra space between characters, mirroring the CSS `letter-spacing` property.
  - Accepts an absolute pixel offset (`letter_spacing(8)`), a percentage of the font's space-character width (`letter_spacing("10%")`), or a `LetterSpacing` instance for type-safe usage.
  - Negative values tighten character spacing.
  - Pass `"normal"` to restore the font's default spacing.
  - Inherited, so it can be set once on a `Canvas` or container and applied to all `Text` nodes inside.

- **Text Box Edge** (`text_box_edge()`): Controls how the top and bottom edges of a text node's bounding box are calculated. Inspired by the CSS `text-box-trim` / `text-box-edge` properties.
  - `"font"` *(default)*: Box edges are derived from the font's ascent/descent metrics - stable and content-independent.
  - `"glyphs"`: Box edges are derived from the actual bounds of the rendered glyphs - tightly wraps visible characters, removing empty ascender/descender space.
  - Shorthand (`text_box_edge("glyphs")`) sets both edges at once. Keyword form (`text_box_edge(top="glyphs")`) sets each edge independently, omitted keywords default to `"font"`.
  - Inherited, so it can be set once on a `Canvas` or container and applied to all `Text` nodes inside.

- **Per-side padding and margin**: Convenience methods to set a single side without touching the others.
  - `padding_top()`, `padding_right()`, `padding_bottom()`, `padding_left()`
  - `padding_horizontal()` (left + right), `padding_vertical()` (top + bottom)
  - `margin_top()`, `margin_right()`, `margin_bottom()`, `margin_left()`
  - `margin_horizontal()` (left + right), `margin_vertical()` (top + bottom)

- **`background_image()`** now accepts a `Path` object in addition to a string, consistent with `font_family()` and `font_fallbacks()`.

### Changed
- **`line_height()`** now takes `"auto"` as default value, meaning each line's vertical space is derived from the font's own metrics (`ascent + descent + leading`). Previously, the default was `1.0 * font_size`, which ignored the font's built-in spacing and was inconsistent with standard typographic behavior.
  > **Visual change**: all existing renders may look different, regardless of whether `.line_height()` was called explicitly. Previously, extra vertical space accumulated entirely below each line. Now it is split evenly: half above the glyphs, half below. This means the text baseline shifts downward by half the vertical space, and lines are vertically centered within their allocated height. **To preserve the previous line heights, call `.line_height(1.0)` explicitly, but be aware the baseline positioning has changed**.

### Fixed
- **Line Height**: Corrected a fundamental mismatch between how line height was stored and how it was applied. Previously, `Line` stored a height derived from font metrics (`ascent + descent + leading`), but painters and layout nodes ignored it when advancing between lines - they independently recomputed `line_height_multiplier * font_size`. This meant the visual spacing and the bounding boxes were driven by two different values, which could cause clipping, misaligned decorations, and incorrect element sizing. `Line.metrics.height` is now the single source of truth for vertical advance, computed once in the shaper and used consistently everywhere.

## [2.1.2] - 2026-03-23

### Fixed
- **Contextual Shaping Across Font Runs**: Scripts like Arabic and Indic that rely on contextual joining (e.g., initial/medial/final character forms) now shape correctly even when a word is split across multiple font runs due to font fallback. Previously, each run was shaped in isolation, causing characters at run boundaries to render in their disconnected (isolated) form instead of the correct joined form.
- **Text Wrapping**: Text nodes with first line empty were not calculating their height correctly.
- **Line Height Calculation**: Line height calculation is now based on the maximum metrics (ascent, descent, leading) of all fonts used in a single line. Previously, it simply used the primary font's metrics, which could result in wrong line heights when using fallback fonts or multiple fonts in the same line.
- **Baseline Alignment**: The text baseline within a line is now determined by the highest ascent of all fonts present in that line. Previously, the baseline was dictated solely by the primary font, causing vertical misalignment when rendering taller fallback fonts (like emojis).
- **Text Decoration Positioning**: The vertical position for underlines and strikethroughs now adapts to the fonts used within the line. Previously, these positions were fixed to the primary font's metrics, which caused decorations to be misaligned or cut through taller fallback characters.
- **Text Direction**: Fixed RTL text rendering where complex ligatures were broken and diacritics misaligned. HarfBuzz now natively processes logical text instead of pre-reversed strings, restoring OpenType GSUB/GPOS features.
- **Text Layout**: Corrected HarfBuzz Y-offset coordinate mapping to Skia's Y-axis, fixing vertically displaced Arabic diacritics.

## [2.1.1] - 2026-03-15

### Fixed
- **Text Wrapping**: Fixed false word-wrapping when no width constraint is set, caused by floating-point precision mismatch between glyph advance measurement and wrapping logic.
- **Text Wrapping**: Fixed CJK text not wrapping within fixed-width containers. Characters from Han, Hiragana, Katakana, and Hangul scripts are now treated as individual breakable units.

## [2.1.0] - 2026-02-18

### Added
- **HarfBuzz Text Shaping**: Integrated `uharfbuzz` for professional text shaping, replacing default Skia shaping.
  - Accurate width calculation for zero-width characters (ZWJ, ZWNJ, BiDi controls).
  - Proper composition of complex emoji sequences (e.g., 👨‍👩‍👧‍👦).
  - Precision glyph positioning using HarfBuzz x/y offsets.
- **BiDi Algorithm**: Automatic Unicode Bidirectional Algorithm (UAX #9) for all text using `python-bidi`.
  - Properly reorders mixed LTR/RTL text (e.g., English + Arabic).
  - Processes BiDi control characters (U+202B, U+202A, U+202C).
  - Automatic detection of text direction from content.
- **Text Direction**: Added `.direction()` method to control horizontal text flow (`"ltr"`, `"rtl"`).
- **`font_weight()`**: Added support for CSS-style string values (e.g., `"bold"`, `"extra-bold"`).
- **Size Methods**: Added `.width()` and `.height()` convenience methods.

### Fixed
- **Text Wrapping**: Fully refactored word wrapping to use HarfBuzz shaping for all token measurements, ensuring pixel-perfect layout.
- **Baseline Alignment**: Fixed vertical alignment issues in lines with multiple fonts by enforcing a common baseline derived from the primary font.

## [2.0.2] - 2026-02-09

### Added
- **Text Stroke Modes**: `text_stroke()` accepts a `mode` parameter (`"center"`, `"outline"`, `"inline"`). Default is `"center"` (CSS-compliant).

### Fixed
- **Text Stroke Bounds**: Fixed an issue where text stroke bounds were not included in the paint bounds, causing strokes to be clipped at the edges.
- **Positioning**: Fixed null layout_result error when using positioning methods.
- **Image Export**: Fixed color type and alpha type conversions when exporting to bytes.
- **to_pillow**: Removed redundant unpremultiply logic since to_numpy now returns unpremultiplied BGRA format.

## [2.0.1] - 2026-01-10

### Fixed
- **positioning**: `place()`, `translate()` and `fixed_position()` were ignoring nested children.

## [2.0.0] - 2026-01-04

### Added
- **Taffy Layout Engine**: Migrated from custom Python layout to `stretchable` (Taffy bindings), providing robust CSS Flexbox layout with improved performance and correctness.
- **CSS-Compliant Positioning System**: Complete overhaul of positioning methods to match CSS standards:
  - **`absolute_position()`**: Position elements relative to their nearest ancestor (like CSS `position: absolute`). Uses `top`, `right`, `bottom`, `left` inset properties.
  - **`fixed_position()`**: Position elements relative to the canvas viewport, ignoring parent positioning (like CSS `position: fixed`). Uses `top`, `right`, `bottom`, `left` inset properties.
  - **`relative_position()`**: Position elements relative to their normal flow position with visual offsets (like CSS `position: relative`). Uses `top`, `right`, `bottom`, `left` inset properties.
  - **`place()`**: Convenience method for anchor-based positioning. Internally uses `fixed_position()` with automatic translate transforms. Supports keywords (`"center"`, `"left"`, `"right"`, `"top"`, `"bottom"`), pixels, percentages, and offsets.
- **Transform Support**: New `translate()` method for post-layout transforms, enabling true centering with percentage-based offsets (e.g., `translate(x="-50%", y="-50%")`).
- **Flex Control Properties**: New methods for fine-grained flexbox control:
  - `flex_grow(value)`: Control how elements grow to fill available space
  - `flex_shrink(value)`: Control how elements shrink when space is limited
  - `align_self(alignment)`: Override container alignment for individual items
  - `flex_wrap(mode)`: Enable multi-line flex containers for responsive layouts
- **Size Constraints**: New methods for controlling element size boundaries:
  - `min_width(value)`: Set minimum width constraint to prevent collapse
  - `max_width(value)`: Set maximum width constraint to prevent overflow
  - `min_height(value)`: Set minimum height constraint to maintain minimum space
  - `max_height(value)`: Set maximum height constraint to limit vertical growth
  - All constraints support both absolute (pixels) and percentage values
- **Aspect Ratio**: New `aspect_ratio(ratio)` method for maintaining element proportions:
  - Automatically calculates height when width is specified (or vice versa)
  - Supports numeric values (e.g., `16/9`, `1.618`) or string format (e.g., `"16/9"`)

### Changed
- **BREAKING**: `position()` method removed. This method positioned elements relative to their **parent** using anchor-based coordinates.
  - **Migration**: Use `absolute_position(top=, left=, right=, bottom=)` with CSS insets for parent-relative positioning.
- **BREAKING**: `absolute_position()` now uses CSS-style inset properties (`top`, `right`, `bottom`, `left`) instead of positional `(x, y)` arguments. It is now **parent-relative** (like CSS `position: absolute`).
  - **Migration options** for old canvas-relative `absolute_position(x, y)`:
    1. Use `place(x, y)` for anchor-based canvas positioning
    2. Use `fixed_position(top=, left=)` for CSS-style canvas positioning
  - **Understanding the difference**:
    - `absolute_position()` is now **parent-relative** (like CSS `position: absolute`)
    - `fixed_position()` and `place()` are **canvas-relative** (like CSS `position: fixed`)
- **BREAKING**: Layout methods renamed to CSS-compliant names:
  - `horizontal_distribution()` → `justify_content()` (Row)
  - `vertical_distribution()` → `justify_content()` (Column)
  - `vertical_align()` → `align_items()` (Row)
  - `horizontal_align()` → `align_items()` (Column)
- **BREAKING**: Removed `'fill-available'` size mode. Use `flex_grow(1)` instead for flexible sizing.
  - **Migration**: Replace `.size(width='fill-available')` with `.flex_grow(1)`
- **BREAKING**: Positioning logic now strictly follows CSS standards.
- **Layout Engine**: All layout calculations now delegated to Taffy, replacing the custom multi-pass algorithm.

### Fixed
- Improved layout correctness for complex nested flexbox scenarios.
- Better handling of percentage-based sizing and positioning.
- Fixed text wrapping on nested nodes.

## [1.5.1] - 2025-12-14

### Added
- **Bundled Default Font**: Inter Variable is now bundled with the package and used as the default font. This prevents issues in environments like Google Colab where system fonts are unavailable.
- **Automatic Font Copying for SVG**: When using `embed_font=False`, font files are now automatically copied to a `fonts/` subdirectory relative to the SVG output path, ensuring SVGs remain portable.

### Changed
- **SVG Font Handling**: Font references in SVG now use relative paths to a `fonts/` subdirectory (e.g., `url('fonts/InterVariable.ttf')`). The `VectorImage.save()` method accepts optional `copy_fonts` and `fonts_subdir` parameters to customize this behavior.

### Fixed
- Avoid usage of deprecated method: `skia.Typeface.MakeDefault()`.
- Added handled exception when unexpected canvas size is received or surface couldn't be created.
- Fixed infinite loop when using `fill-available` size mode in `Row` or `Column` with children using percentage size mode.

## [1.5.0] - 2025-10-05

### Added
- **Gradient Support**: Added support for advanced gradient fills
  - `RadialGradient`: Circular gradients from center point outward
  - `SweepGradient`: Conical gradients sweeping around a center point
  - `TwoPointConicalGradient`: Gradients transitioning between two circles with different radii
- **Font Rendering Enhancements**: Enabled linear metrics, auto hinting, and slight hinting to improve text quality and consistency across platforms

### Changed
- **SVG Font References**: When using `embed_font=False` in `render_as_svg()`, font file references now use only the filename (e.g., `'font.ttf'`) instead of absolute paths. This improves portability and assumes fonts are placed in the same directory as the SVG file.

### Fixed
- Avoid font family name normalization on system fonts used in SVGs.
- Fixed fallback font behavior: fallback fonts are now used when the primary font is not found, rather than falling back to default system font.
- Fixed text line height calculation to account for all fonts used in each line, not just the primary font. This ensures correct vertical spacing when fallback fonts are used.
- Fixed bug when no system font is found for specific grapheme during falling back process

## [1.4.0] - 2025-09-29

### Added

- Added comprehensive type annotations and mypy static type checking integration
- **NamedColor Enum**: Exposed `NamedColor` enum class to improve developer experience when using colors. The enum provides easy access to all supported named colors with autocompletion and type safety.
- **Text Shaping Support**: Added advanced text shaping capabilities including kerning, ligatures, and proper complex script rendering (Arabic, emoji sequences). Text now renders with correct character connections and spacing adjustments.

### Fixed

- Fixed SVG rendering with custom font files being embedded. It was not working because a wrong SVG tag was being used.
- Fixed SVG font family normalization by removing spaces and commas from font identifiers to prevent rendering issues.
- Fixed text wrapping when no width constraint is specified, avoiding unnecessary wrap calculations.

### Changed

- Exclude development files from package distribution (/.github, /docs, /examples, /tests, .gitignore, *.yml, *.yaml)
- **BREAKING**: `text_stroke()` behavior now aligns with CSS standards. The stroke is now rendered centered on the text outline (half inside, half outside) instead of only outward. This matches `-webkit-text-stroke` behavior but will make stroked text appear visually thicker. Existing designs using this feature may need adjustment.

## [1.3.3] - 2025-09-27

### Fixed

- Fixed `RuntimeError: Failed to get; Likely no parameter` when using static font file. This error is happening only in some cases (maybe because of the font file, system, or skia version).

## [1.3.1] - 2025-09-14

### Fixed

- Fixed transparency handling in `BitmapImage.to_pillow()` method. The method now properly unpremultiplies alpha values from Skia's premultiplied format to Pillow's straight alpha format.

## [1.3.0] - 2025-09-13

### Added

- **Render Tree Access**: Both `BitmapImage` and `VectorImage` now expose a `render_tree` property that provides access to the hierarchical structure of rendered nodes with their bounds information. This allows users to inspect and interact with individual elements after rendering.
- **NodeType Enum**: New `NodeType` enum with values `TEXT`, `ROW`, `COLUMN`, and `ELEMENT` for type-safe node identification.
- **RenderNode Class**: New `RenderNode` class that represents nodes in the render tree, featuring:
  - `bounds`: Bounding box information for each node
  - `children`: Access to child nodes in the hierarchy
  - `node_type`: Type-safe node identification using `NodeType` enum
  - `visit_children()`: Method to recursively traverse child nodes
  - `find_nodes_by_type()`: Method to find all nodes of a specific type
- **Scale Factor Support**: New `scale_factor` parameter in `Canvas.render()` method allows rendering images at larger sizes. All dimensions (width, height, fonts, etc.) are scaled proportionally.
- **Extended Named Colors**: Added support for many additional named colors including extended CSS color names.

## [1.2.1] - 2025-09-07

### Fixed

- Fixed a major layout bug causing incorrect text wrapping in containers with multiple flexible children (e.g., a `Row`). Text now correctly calculates its available width based on siblings, preventing overflow.

## [1.2.0] - 2025-09-06

### Added

- New `'fill-available'` size mode allows elements to grow and fill the remaining space within a `Row` or `Column`, enabling more complex and fluid layouts.
- **Text Wrapping**: Added automatic text wrapping support. Text now automatically wraps to multiple lines when placed in containers with fixed widths. A new `.text_wrap()` method controls this behavior with `"normal"` (default, wrapping enabled) and `"nowrap"` (wrapping disabled) values.

### Fixed

- Use `position()`/`absolute_position()` in container (row or column) with children was causing unexpected exception

## [1.1.1] - 2025-08-09

### Fixed

- Fixed `stretch` alignment in Row/Column with nested descendants (two or more levels) causing unexpected exceptions

## [1.1.0] - 2025-08-09

### Added

- Documentation for builder classes was improved
- Support `stretch` for `horizontal_align()` and `vertical_align()` in `Row` and `Column` builders

### Changed

- Width and height are not calculated indivdually, it allows using parent with `fit-content` width (or height) and children with `percent` width (or height). For example, last version didn't admit child with `50%` width if the parent has fixed width but `fit-content` height.

### Fixed

- Render empty text line was throwing an unexpected exception

## [1.0.0] - 2025-08-04

### Added

-   **Component-Based Layout Engine**: PicTex is now a full-fledged layout engine. You can compose complex visuals by nesting `Row`, `Column`, `Text`, and `Image` builders.
-   **Layout Builders**: New `Row` and `Column` builders to arrange elements horizontally or vertically.
-   **Layout Control**:
    -   New `.horizontal_distribution()` and `.vertical_distribution()` methods for `Row` and `Column` to control main-axis spacing (`center`, `space-between`, etc.).
    -   New `.vertical_align()` and `.horizontal_align()` methods for `Row` and `Column` to control cross-axis alignment.
    -   New `.gap()` method on containers to set a consistent space between children.
-   **`Image` Builder**: A new first-class builder for adding and styling images.
-   **Sizing System**:
    -   New `.size()` method on all builders to set explicit dimensions.
    -   Support for `'fit-content'`, `'fit-background-image'`, and percentage (`'50%'`) sizing modes.
-   **Positioning System**:
    -   New `.position()` method to position an element relative to its parent's content area.
    -   New `.absolute_position()` method to position an element relative to the root canvas.
-   **Border Support**: New `.border()` method to add borders with `width`, `color`, and `style` (`'solid'`, `'dashed'`, `'dotted'`).
-   **Background Images**: New `.background_image()` method to set a background on any element, with support for `'cover'`, `'contain'`, and `'tile'` modes.

### Changed

-   **BREAKING**: The shadow API is now declarative.
    -   `add_text_shadow()` is replaced by `text_shadows(*shadows: Shadow)`.
    -   `add_box_shadow()` is replaced by `box_shadows(*shadows: Shadow)`.
    -   **Migration**: You must now import and instantiate the `Shadow` class, e.g., `.text_shadows(Shadow(offset=(2,2)))`. This allows multiple shadows to be set in a single call and enables overriding.
-   **BREAKING**: The `background_radius()` method was renamed to `.border_radius()`. It now accepts percentage values (e.g., `'50%'`) and can take 1, 2, or 4 arguments to control each corner individually.
-   **BREAKING**: The `Canvas()` constructor can't receive a `Style` instance anymore.
-   **BREAKING**: The `outline_stroke()` method was renamed to `text_stroke()`.
-   **BREAKING**: The `alignment()` method was renamed to `text_align()`.
-   **BREAKING**: The default padding was changed from `10` to `0`.
-   **BREAKING**: Each text box now has a larger height than before.
-   **BREAKING**: Shadows are ignored when the result is exported as an SVG image. It was supported in version 0.3.x.

## [0.3.1] - 2025-08-03

### Added

- Documentation for user-facing classes was improved

## [0.3.0] - 2025-07-16

### Added

- Render image as SVG. A new method was added in the Canvas class: `render_as_svg()`.
- If a character can't be rendered by the fonts provided, a system font for it will be searched.

### Fixed

- **Bug in font fallbacks**: when a font fallback was used for a glyph, the next characters was also rendered using the fallback, even when the primary font supported them (more info on issue #2).

### Changed
- `Canvas.font_family(...)` and `Canvas.font_fallbacks(...)` now support a `Path` object instance in addition to a string.
- The default font family now is the system font (it was `Arial`)
- If the primary font or any fallback font is not found, a warning is generated, and that font is ignored.

## [0.2.1] - 2025-07-10

### Added

- **Configurable Font Smoothing:** Added a `.font_smoothing()` method to the `Canvas` to control the text anti-aliasing strategy. This allows users to choose between `'subpixel'` (default, for maximum sharpness on LCDs) and `'standard'` (grayscale, for universal compatibility).

### Fixed

- **Text Rendering Quality:** Resolved a major issue where text could appear aliased or pixelated. The new default font smoothing (`'subpixel'`) ensures crisp, high-quality text output out-of-the-box.

## [0.2.0] - 2025-07-10

### Added

- **Font Fallback System:** Implemented a robust font fallback mechanism. `pictex` now automatically finds a suitable font for characters not present in the primary font, including emojis and special symbols. A `canvas.font_fallbacks()` method was added for user-defined fallbacks.

## [0.1.0] - 2025-07-09

- Initial release.
