import skia
from ..models import Style, CropMode
from .shaper import TextShaper
from .font_manager import FontManager
from .metrics_calculator import MetricsCalculator
from .painters import Painter, BackgroundPainter, DecorationPainter, TextPainter
from .image_processor import ImageProcessor
from .vector_image_processor import VectorImageProcessor
from .structs import RenderMetrics
from ..image import Image
from ..vector_image import VectorImage
from typing import Tuple

class Renderer:
    def __init__(self, style: Style):
        self._style = style

    def render_as_bitmap(self, text: str, crop_mode: CropMode) -> Image:
        """Renders the text with the given style, generating a bitmap image."""
        font_manager = FontManager(self._style)
        shaper = TextShaper(self._style, font_manager)
        metrics_calculator = MetricsCalculator(self._style, font_manager)
        lines = shaper.shape(text)
        metrics = metrics_calculator.calculate(lines, crop_mode)

        width, height = self._validate_canvas_size(metrics)
        image_info = skia.ImageInfo.MakeN32Premul(width, height)
        surface = skia.Surface(image_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(metrics.draw_origin[0], metrics.draw_origin[1])

        for PainterClass in self._get_painters():
            p: Painter = PainterClass(self._style, metrics, font_manager)
            p.paint(canvas, lines)
        
        del canvas
        final_image = surface.makeImageSnapshot()
        return ImageProcessor().process(final_image, metrics, crop_mode)
    
    def render_as_svg(self, text: str, embed_fonts: bool) -> VectorImage:
        """Renders the text with the given style, generating a vector image."""
        font_manager = FontManager(self._style)
        shaper = TextShaper(self._style, font_manager)
        metrics_calculator = MetricsCalculator(self._style, font_manager)
        lines = shaper.shape(text)
        metrics = metrics_calculator.calculate(lines, CropMode.NONE)

        stream = skia.DynamicMemoryWStream()
        width, height = self._validate_canvas_size(metrics)
        bounds = skia.Rect(0, 0, width, height)
        canvas = skia.SVGCanvas.Make(bounds, stream)
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(metrics.draw_origin[0], metrics.draw_origin[1])

        for PainterClass in self._get_painters():
            p: Painter = PainterClass(self._style, metrics, font_manager, True)
            p.paint(canvas, lines)

        del canvas
        return VectorImageProcessor().process(stream, embed_fonts, lines, self._style)
    
    def _validate_canvas_size(self, metrics: RenderMetrics) -> Tuple[int, int]:
        width = int(metrics.bounds.width())
        height = int(metrics.bounds.height())
        if width <= 0 or height <= 0:
            raise ValueError(f"Unexpected bounds: [width={width}, height={height}]. Image without text?")
        return (width, height)

    def _get_painters(self) -> list:
        # to keep in mind: the orders of the painters is important!
        return [
            BackgroundPainter,
            TextPainter,
            DecorationPainter,
        ]
