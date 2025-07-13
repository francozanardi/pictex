import skia
from typing import Tuple
from ..models import Style, CropMode, Box
from .shaper import TextShaper
from .font_manager import FontManager
from .metrics_calculator import MetricsCalculator
from .painters import Painter, BackgroundPainter, DecorationPainter, TextPainter
from .image_processor import ImageProcessor

class SkiaRenderer:
    """Handles the drawing logic using Skia."""

    def __init__(self, style: Style):
        self._style = style

    def render(self, text: str, crop_mode: CropMode) -> Tuple[skia.Image, Box]:
        """Renders the text with the given style onto a perfectly sized Skia surface."""

        font_manager = FontManager(self._style)
        shaper = TextShaper(self._style, font_manager)
        metrics_calculator = MetricsCalculator(self._style, font_manager)
        # to keep in mind: the orders of the painters is important!
        painters = [
            BackgroundPainter,
            TextPainter,
            DecorationPainter,
        ]

        lines = shaper.shape(text)
        metrics = metrics_calculator.calculate(lines, crop_mode)

        canvas_width = int(metrics.bounds.width())
        canvas_height = int(metrics.bounds.height())
        if canvas_width <= 0 or canvas_height <= 0:
            return skia.Image.MakeRasterN32Premul(1, 1)

        image_info = skia.ImageInfo.MakeN32Premul(canvas_width, canvas_height)
        surface = skia.Surface(image_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        canvas.translate(metrics.draw_origin[0], metrics.draw_origin[1])

        for PainterClass in painters:
            p: Painter = PainterClass(self._style, metrics, font_manager)
            p.paint(canvas, lines)
        
        final_image = surface.makeImageSnapshot()
        return ImageProcessor().process(final_image, metrics, crop_mode)
