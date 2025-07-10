# CHANGELOG

## v0.2.0 - 07/10/2025

### Features

-   **Font Fallback System:** Implemented a robust font fallback mechanism. `pictex` now automatically finds a suitable font for characters not present in the primary font, including emojis and special symbols. A `canvas.font_fallbacks()` method was added for user-defined fallbacks.

### Refactor

-   **Modular Renderer:** The monolithic `SkiaRenderer` has been refactored into a modular `renderer` package. This greatly improves maintainability, testability, and code clarity.

## v0.1.0 - 07/09/2025

-   Initial release.