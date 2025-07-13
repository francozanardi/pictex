from ...models import Alignment

def get_line_x_position(line_width: float, block_width: float, align: Alignment) -> float:
    if align == Alignment.RIGHT:
        return block_width - line_width
    if align == Alignment.CENTER:
        return (block_width - line_width) / 2
    
    return 0 # Alignment.LEFT
