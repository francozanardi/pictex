from abc import ABC, abstractmethod
from ..models import Style
import skia

class Painter(ABC):
    
    def __init__(self, style: Style):
        self._style: Style = style

    @abstractmethod
    def paint(self, canvas: skia.Canvas) -> None:
        raise NotImplemented()
