from .stylable import Stylable
from ..nodes import Node

class Element(Stylable):

    def _to_node(self) -> Node:
        raise NotImplementedError()
