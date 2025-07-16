from __future__ import annotations

class VectorImage:
    """
    Represents a rendered vector image in SVG format.

    This class provides the SVG content as a string and convenient methods
    for saving it to a file or displaying it in environments like Jupyter.
    """
    def __init__(self, svg_content: str):
        """
        Initializes the VectorImage. Typically created by `Canvas.render_as_svg()`.

        Args:
            svg_content: The full SVG content as a string.
        """
        self._svg_content = svg_content

    @property
    def svg(self) -> str:
        """Returns the raw SVG content as a string."""
        return self._svg_content

    def save(self, output_path: str) -> None:
        """
        Saves the SVG image to a file.

        Args:
            output_path: The path to save the output file (e.g., 'image.svg').
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self._svg_content)
    
    def __str__(self) -> str:
        """Allows `print(vector_image)` to show the SVG content."""
        return self._svg_content

    def _repr_svg_(self) -> str:
        """
        Jupyter magic method. Allows the object to be displayed directly as
        an SVG image in a notebook cell.
        """
        return self._svg_content
