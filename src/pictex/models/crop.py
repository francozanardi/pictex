from enum import Enum

class CropMode(Enum):
    """
    Defines how the final image canvas should be cropped.
    """
    SMART = "smart"
    CONTENT_BOX = "content_box"
    NONE = "none"
