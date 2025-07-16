# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
