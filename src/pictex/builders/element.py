from .stylable import Stylable
from .with_position_mixin import WithPositionMixin
from .with_size_mixin import WithSizeMixin
from ..nodes import Node

class Element(Stylable, WithPositionMixin, WithSizeMixin):

    def _to_node(self) -> Node:
        raise NotImplementedError()
