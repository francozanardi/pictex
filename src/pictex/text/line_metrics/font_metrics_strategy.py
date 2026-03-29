from ...models import LineMetrics, TextRun
from .metrics_strategy import AggregatedLineFontsMetrics, LineMetricsStrategy


class FontMetricsStrategy(LineMetricsStrategy):
    """Sizes a line edge using the font's metrics.

    The edge position is determined solely by the font,
    making layouts stable and predictable regardless of text content.
    Applies ``vertical_space`` to its edge to honour the ``line_height`` setting.
    """

    def calculate(
        self,
        runs: list[TextRun],
        metrics: AggregatedLineFontsMetrics
    ) -> LineMetrics:
        return LineMetrics(
            height=metrics.ascent + metrics.descent + (metrics.vertical_space * 2),
            baseline=metrics.ascent + metrics.vertical_space,
            underline=metrics.underline_from_top + metrics.vertical_space,
            strikethrough=metrics.strikethrough_from_top + metrics.vertical_space,
        )
