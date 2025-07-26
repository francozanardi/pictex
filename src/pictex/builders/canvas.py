from __future__ import annotations
from typing import Union
from .element import Element
from .row import Row
from .stylable import Stylable
from ..models import *
from ..image import Image
from ..vector_image import VectorImage
from ..renderer import Renderer
from .with_size_mixin import WithSizeMixin

class Canvas(Stylable, WithSizeMixin):
    """The main user-facing class for creating stylized text images.

    This class implements a fluent builder pattern to define a builders template,
    which can then be used to render multiple texts. Each styling method returns
    the instance of the class, allowing for method chaining.

    Example:
        ```python
        canvas = Canvas()
        image = (
            canvas.font_family("Arial")
            .font_size(24)
            .color("blue")
            .add_shadow(offset=(2, 2), blur_radius=3, color="black")
            .render("Hello, World!")
        )
        image.save("output.png")
        ```
    """

    def render(
            self,
            *elements: Union[Element, str],
            crop_mode: CropMode = CropMode.NONE,
            font_smoothing: Union[FontSmoothing, str] = FontSmoothing.SUBPIXEL,
    ) -> Image:
        """Renders an image from the given elements using the configured builders.

        Args:
            elements: The elements to be rendered. The strings received are converted to Text elements.
            crop_mode: The cropping strategy for the final canvas.
                - `SMART`: Tightly crops to only visible pixels.
                - `CONTENT_BOX`: Crops to the text + padding area.
                - `NONE`: No cropping, includes all effect boundaries (default).
            font_smoothing: The font smoothing mode. Accepts either `FontSmoothing.SUBPIXEL`
                or `FontSmoothing.STANDARD`, or their string equivalents (`"subpixel"` or `"standard"`).

        Returns:
            An `Image` object containing the rendered result.
        """
        font_smoothing = font_smoothing if isinstance(font_smoothing, FontSmoothing) else FontSmoothing(font_smoothing)
        renderer = Renderer()
        element = Row(*elements)
        element._style = self._style
        root = element._to_node()
        return renderer.render_as_bitmap(root, crop_mode, font_smoothing)

    # def render_as_svg(self, *elements: Union[Element, str], embed_font: bool = True) -> VectorImage:
    #     """Renders the given elements as a scalable vector graphic (SVG).
    #
    #     This method produces a vector-based image, ideal for web use and
    #     applications requiring resolution independence.
    #
    #     Args:
    #         elements: The elements to be rendered. The strings received are converted to Text elements.
    #         embed_font: If `True` (default), any custom font files (`.ttf`/`.otf`)
    #             provided will be embedded directly into the SVG. This
    #             ensures perfect visual fidelity across all devices but
    #             increases file size. A warning will be issued if a system
    #             font is used with this option enabled. If `False`, the SVG will
    #             reference the font by name, relying on the viewing system to
    #             have the font installed.
    #
    #     Returns:
    #         A `VectorImage` object containing the SVG data.
    #     """
    #     renderer = Renderer()
    #     root = Row(*elements)._to_node()
    #     return renderer.render_as_svg(root, embed_font)
