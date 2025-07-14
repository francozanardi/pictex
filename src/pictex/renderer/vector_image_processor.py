import skia
from ..vector_image import VectorImage
import base64
import re
from .structs import Line, TypefaceSource, TypefaceLoadingInfo
import warnings
from ..exceptions import SystemFontCanNotBeEmbeddedInSvgWarning
from .typeface_loader import TypefaceLoader

class VectorImageProcessor:
    
    def process(self, stream: skia.DynamicMemoryWStream, embed_fonts: bool, lines: list[Line]) -> VectorImage:
        data = stream.detachAsData()
        svg = bytes(data).decode("utf-8")
        fonts = self._get_used_fonts(lines)
        typefaces = self._map_to_file_typefaces(fonts, embed_fonts)
        svg = self._embed_fonts_in_svg(svg, typefaces, embed_fonts)
        return VectorImage(svg)
    
    def _get_used_fonts(self, lines: list[Line]) -> list[skia.Font]:
        fonts = []
        for line in lines:
            for run in line.runs:
                if run.font not in fonts:
                    fonts.append(run.font)

        return fonts
    
    def _map_to_file_typefaces(self, fonts: list[skia.Font], should_warn_for_system_fonts: bool) -> list[TypefaceLoadingInfo]:
        typefaces = []
        for font in fonts:
            loading_info = TypefaceLoader.get_typeface_loading_info(font.getTypeface())
            if not loading_info:
                # TODO: use logging.error / logging.warn to avoid break the execution
                # raise RuntimeError(
                #     f"Unexpected error. Font '{font.getTypeface().getFamilyName()}' was "
                #     "loaded without using TypefaceLoader?"
                # )
                continue
       
            if loading_info.source == TypefaceSource.SYSTEM:
                if should_warn_for_system_fonts:
                    warning_message = (
                        f"Font '{font.getTypeface().getFamilyName()}' is a system font and cannot be embedded. "
                        "The SVG will rely on the font being installed on the viewer's system."
                    )
                    warnings.warn(warning_message, SystemFontCanNotBeEmbeddedInSvgWarning)
                continue

            typefaces.append(loading_info)
        return typefaces
    
    def _embed_fonts_in_svg(self, svg: str, typefaces: list[TypefaceLoadingInfo], embed_fonts: bool) -> str:
        css = self._get_css_code_for_typefaces(typefaces, embed_fonts)
        defs = f"""
<defs>
    <style type="text/css">
        {css}
    </style>
</defs>
            """

        svg_tag_pattern = re.compile(r"<svg[^>]*>")
        match = svg_tag_pattern.search(svg)
        if not match:
            # TODO: use logging.error / logging.warn to avoid break the execution
            # raise RuntimeError(f"Unexpected error. Invalid SVG content: '{svg_content}'")
            return svg

        insert_position = match.end()
        svg = (
            svg[:insert_position] +
            defs +
            svg[insert_position:]
        )
        svg = self._add_prefix_to_font_families(svg, typefaces)
        return svg

    def _get_css_code_for_typefaces(self, typefaces: list[TypefaceLoadingInfo], embed_fonts: bool) -> str:
        format_map = {
            "ttf": "truetype",
            "otf": "opentype",
            "woff": "woff",
            "woff2": "woff2",
        }
        
        css = ""
        for typeface in typefaces:
            filepath = typeface.filepath
            try:
                with open(filepath, "rb") as font_file:
                    font_data = font_file.read()
            except IOError as e:
                continue
            
            src = filepath
            if embed_fonts:
                encoded_font = base64.b64encode(font_data).decode("utf-8")
                file_extension = filepath.lower().split('.')[-1]
                font_format = format_map.get(file_extension, "truetype")
                src = f"data:font/{file_extension};base64,{encoded_font}') format('{font_format}"

            css += f"""
@font-face {{
    font-family: '{typeface.typeface.getFamilyName()}';
    src: url('{src}');
}}
            """
        
        return css
    
    def _add_prefix_to_font_families(self, svg: str, typefaces: list[TypefaceLoadingInfo]) -> str:
        for typeface in typefaces:
            font_family = typeface.typeface.getFamilyName()
            svg = svg.replace(f"'{font_family}'", f"'pictex-{font_family}'")
            svg = svg.replace(f'"{font_family}"', f'"pictex-{font_family}"')
        return svg
