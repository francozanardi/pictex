from .stylable import Stylable
from .positionable import PositionableMixin
from ..nodes import Node

class Element(Stylable, PositionableMixin):

    def _to_node(self) -> Node:
        raise NotImplementedError()
