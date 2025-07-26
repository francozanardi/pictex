from dataclasses import dataclass
from typing import Tuple, Optional, NamedTuple, Literal

class SizeValue(NamedTuple):
    mode: Literal['absolute', 'percent', 'fit-content']
    value: float = 0

@dataclass
class Size:
    width: SizeValue
    height: SizeValue

    def get_final_size(
            self,
            content_width: float,
            content_height: float,
            container_width: Optional[float],
            container_height: Optional[float],
    ) -> Tuple[float, float]:
        final_width, final_height = None, None

        if self.width.mode == 'absolute':
            final_width = self.width.value
        elif self.width.mode == 'percent':
            if container_width is None:
                raise ValueError(
                    "Container width is required for percentage-based width but was not provided."
                )
            final_width = container_width * (self.width.value / 100.0)
        elif self.width.mode == 'fit-content':
            final_width = content_width

        if self.height.mode == 'absolute':
            final_height = self.height.value
        elif self.height.mode == 'percent':
            if container_height is None:
                raise ValueError(
                    "Container height is required for percentage-based height but was not provided."
                )
            final_height = container_height * (self.height.value / 100.0)
        elif self.height.mode == 'fit-content':
            final_height = content_height

        if final_width is None or final_height is None:
            raise ValueError(f"Unable to calculate size ({final_width}, {final_height}).)")

        return final_width, final_height
