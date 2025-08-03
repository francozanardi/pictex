from ..models import TextAlign

def get_line_x_position(line_width: float, block_width: float, align: TextAlign) -> float:
    if align == TextAlign.RIGHT:
        return block_width - line_width
    if align == TextAlign.CENTER:
        return (block_width - line_width) / 2
    
    return 0 # Alignment.LEFT
