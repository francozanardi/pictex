from ..models import RenderNode, NodeType, Box
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..nodes import Node

def create_render_tree(node: "Node") -> RenderNode:
    """Creates a RenderNode tree from the internal node structure.
    
    Args:
        node: The internal Node to convert.
        
    Returns:
        A RenderNode representing the node and its children.
    """
    from ..nodes import RowNode, ColumnNode, TextNode

    # Determine node type
    if isinstance(node, TextNode):
        node_type = NodeType.TEXT
    elif isinstance(node, RowNode):
        node_type = NodeType.ROW
    elif isinstance(node, ColumnNode):
        node_type = NodeType.COLUMN
    else:
        node_type = NodeType.ELEMENT
    
    # Get bounds from border_bounds (equivalent to border bounds)
    bounds_rect = node.border_bounds
    node_position = node.absolute_position
    if not node_position:
        raise RuntimeError("Unexpected node position value: node.absolute_position is not defined.")

    bounds = Box(
        x=int(bounds_rect.left() + node_position[0]),
        y=int(bounds_rect.top() + node_position[1]),
        width=int(bounds_rect.width()),
        height=int(bounds_rect.height())
    )
    
    # Recursively create children
    children = [create_render_tree(child) for child in node.children]
    
    return RenderNode(
        bounds=bounds,
        children=children,
        node_type=node_type
    )
