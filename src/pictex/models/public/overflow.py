from enum import Enum


class Overflow(Enum):
    """Controls how content that exceeds a node's bounds is handled.

    Equivalent to CSS ``overflow``.

    Values:
        VISIBLE: Content is not clipped and may render outside the node's
            padding box. This is the default behaviour.
        HIDDEN: Content that exceeds the node's padding box is clipped and
            hidden. Children of a container node and the rendered text of a
            text node are both subject to clipping.
    """

    VISIBLE = "visible"
    HIDDEN = "hidden"
