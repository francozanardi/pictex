from dataclasses import dataclass
from ..models import Style


@dataclass
class SpanNode:
    """An inline text fragment with its own raw style.

    Produced by ``Span._to_node()`` and consumed by ``TextNode``.
    This is a pure data holder - it does not participate in the flex layout tree.
    """
    text: str
    style: Style
