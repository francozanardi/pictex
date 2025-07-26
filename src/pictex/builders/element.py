from .stylable import Stylable
from .with_position_mixin import WithPositionMixin
from ..nodes import Node

class Element(Stylable, WithPositionMixin):

    def _to_node(self) -> Node:
        raise NotImplementedError()
