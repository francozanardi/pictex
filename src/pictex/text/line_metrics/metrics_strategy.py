from abc import ABC, abstractmethod
from attr import dataclass
from ...models import LineMetrics, TextRun


@dataclass(frozen=True)
class AggregatedLineFontsMetrics:
    ascent: float
    descent: float
    vertical_space: float
    underline_from_top: float
    strikethrough_from_top: float


class LineMetricsStrategy(ABC):
    """Defines how one edge (top or bottom) of a text line's box is sized.

    Each strategy is responsible for a single edge.
    """

    @abstractmethod
    def calculate(
        self,
        runs: list[TextRun],
        aggregated_metrics: AggregatedLineFontsMetrics
    ) -> LineMetrics:
        """Compute LineMetrics for a set of shaped runs.

        Args:
            runs: The shaped text runs that form the line (shaped_glyphs must be set).
            aggregated_metrics: Aggregated metrics for the line.

        Returns:
            Computed LineMetrics.
        """
