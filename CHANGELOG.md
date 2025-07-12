# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
