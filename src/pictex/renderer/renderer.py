import skia
from ..models import FontSmoothing
from ..models import Style, CropMode
from .image_processor import ImageProcessor
from ..models import RenderProps
from ..bitmap_image import BitmapImage
from ..nodes import Node


class Renderer:
    # def __init__(self, style: Style):
    #     self._style = style

    def render_as_bitmap(self, root: Node, crop_mode: CropMode, font_smoothing: FontSmoothing) -> BitmapImage:
        """Renders the nodes with the given builders, generating a bitmap image."""
        root.prepare_tree_for_rendering(RenderProps(False, crop_mode, font_smoothing))

        canvas_bounds = root.paint_bounds
        image_info = skia.ImageInfo.MakeN32Premul(int(canvas_bounds.width()), int(canvas_bounds.height()))
        surface = skia.Surface(image_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(-canvas_bounds.left(), -canvas_bounds.top())

        root.paint(canvas)
        del canvas
        final_image = surface.makeImageSnapshot()
        return ImageProcessor().process(root, final_image, crop_mode)
    
    # def render_as_svg(self, root: Node, embed_fonts: bool) -> VectorImage:
    #     """Renders the text with the given builders, generating a vector image."""
    #     canvas_bounds = root.paint_bounds
    #     stream = skia.DynamicMemoryWStream()
    #     canvas = skia.SVGCanvas.Make(canvas_bounds, stream)
    #
    #     canvas.clear(skia.ColorTRANSPARENT)
    #     canvas.translate(-canvas_bounds.left(), -canvas_bounds.top())
    #
    #     root.prepare(RenderProps(False, CropMode.NONE, FontSmoothing.SUBPIXEL))
    #     root.paint(canvas)
    #
    #     del canvas
    #     return VectorImageProcessor().process(stream, embed_fonts, lines, self._style)
