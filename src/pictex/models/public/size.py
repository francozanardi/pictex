from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, NamedTuple

class SizeValueMode(str, Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
    FIT_CONTENT = 'fit-content'
    FIT_BACKGROUND_IMAGE = 'fit-background-image'

class SizeValue(NamedTuple):
    mode: SizeValueMode
    value: float = 0

@dataclass
class Size:
    width: SizeValue
    height: SizeValue

    def get_final_size(
            self,
            content_width: float,
            content_height: float,
            container_width: Optional[float] = None,
            container_height: Optional[float] = None,
    ) -> Tuple[float, float]:
        final_width = self._get_axis_size(self.width, content_width, container_width)
        final_height = self._get_axis_size(self.height, content_height, container_height)

        if final_width is None or final_height is None:
            raise ValueError(f"Unable to calculate size ({final_width}, {final_height}).)")

        return final_width, final_height

    def _get_axis_size(self, value: SizeValue, content_value: float, container_value: float) -> Optional[float]:
        if value.mode == 'absolute':
            return value.value
        if value.mode == 'percent':
            if container_value is None:
                raise ValueError(
                    "Container size is required for percentage-based size but was not provided."
                )
            return container_value * (value.value / 100.0)
        if value.mode == 'fit-content':
            return content_value

        return None