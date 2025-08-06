# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Documentation for builder classes was improved

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
