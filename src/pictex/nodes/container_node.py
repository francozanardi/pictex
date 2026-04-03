from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style


class ContainerNode(Node):
    """Base class for container nodes that can have children."""

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)

    def _get_decoration_painters(self) -> list[Painter]:
        """Return painters for container background and border."""
        if not self._render_props:
            raise RuntimeError("_render_props not initialized - call prepare_tree_for_rendering first")

        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
        ]

    def compute_intrinsic_width(self) -> int:
        """Compute intrinsic width (sum/max of children depending on layout direction)."""
        # For containers with children, stretchable calculates size from children
        return 0
    
    def compute_intrinsic_height(self) -> int:
        """Compute intrinsic height (sum/max of children depending on layout direction)."""
        # For containers with children, stretchable calculates size from children
        return 0
