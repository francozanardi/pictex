from ...models import DecorationLine
import skia

def decoration_line_to_line_y_offset(decoration_line: DecorationLine, font_metrics: skia.FontMetrics) -> float:
    if decoration_line == DecorationLine.UNDERLINE:
        return font_metrics.fUnderlinePosition
    
    return font_metrics.fStrikeoutPosition
