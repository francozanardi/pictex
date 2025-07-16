from abc import ABC, abstractmethod
from ...models import Style
from ..structs import RenderMetrics, Line
from ..font_manager import FontManager
import skia

class Painter(ABC):
    
    def __init__(self, style: Style, metrics: RenderMetrics, font_manager: FontManager, is_svg: bool = False):
        self._style: Style = style
        self._metrics: RenderMetrics = metrics
        self._font_manager: FontManager = font_manager
        self._is_svg = is_svg

    @abstractmethod
    def paint(self, canvas: skia.Canvas, lines: list[Line]) -> None:
        raise NotImplemented()
