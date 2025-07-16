import skia
import base64
import re
from .structs import Line, TypefaceSource, TypefaceLoadingInfo
import warnings
from ..exceptions import SystemFontCanNotBeEmbeddedInSvgWarning
from .typeface_loader import TypefaceLoader
import xml.etree.ElementTree as ET
from ..vector_image import VectorImage
from ..models import Shadow, Style
from typing import Optional
import os

class VectorImageProcessor:
    
    def process(self, stream: skia.DynamicMemoryWStream, embed_fonts: bool, lines: list[Line], style: Style) -> VectorImage:
        data = stream.detachAsData()
        svg = bytes(data).decode("utf-8")
        fonts = self._get_used_fonts(lines)
        typefaces = self._map_to_file_typefaces(fonts, embed_fonts)
        svg = self._fix_text_attributes(svg, typefaces)
        svg = self._add_shadows(svg, style)
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
            # raise RuntimeError(f"Unexpected error. Invalid SVG content: '{svg}'")
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
            font_family = self._get_svg_family_name(typeface.typeface)
            filepath = typeface.filepath
            try:
                with open(filepath, "rb") as font_file:
                    font_data = font_file.read()
            except IOError as e:
                continue
            
            src = os.path.normpath(filepath).replace("\\", "/")
            if embed_fonts:
                encoded_font = base64.b64encode(font_data).decode("utf-8")
                file_extension = filepath.lower().split('.')[-1]
                font_format = format_map.get(file_extension, "truetype")
                src = f"data:font/{file_extension};base64,{encoded_font}') format('{font_format}"

            css += f"""
@font-face {{
    font-family: '{font_family}';
    src: url('{src}');
}}
            """
        
        return css

    def _get_svg_family_name(self, typeface: skia.Typeface) -> str:
        family_names = list(map(lambda fn: fn[0], typeface.getFamilyNames()))
        return ", ".join(family_names)
    
    def _add_prefix_to_font_families(self, svg: str, typefaces: list[TypefaceLoadingInfo]) -> str:
        for typeface in typefaces:
            font_family = self._get_svg_family_name(typeface.typeface)
            svg = svg.replace(f"'{font_family}'", f"'pictex-{font_family}'")
            svg = svg.replace(f'"{font_family}"', f'"pictex-{font_family}"')
        return svg
    
    def _fix_text_attributes(self, svg: str, typefaces: list[TypefaceLoadingInfo]) -> str:
        """
        It applies two different fixes over the SVG generated via Skia:
        1. Removes the <text> font-x style attributes in static fonts
           When you load a static font, let's say Lato-Bold.ttf, it already includes the weight statically.
           However, the SVG generated by Skia is adding the attribute "font-weight" to <text>.
           This causes that some SVG viewers (like a Chrome browser) add extra faux weights (because of the argument).
           These style arguments are not needed, since font is static and those styles are already included.
           We need to remove them, otherwise the SVG generated will be different from the PNG, and it can overflow the bounds of the SVG.
        2. If "font-weight" is present on <text>, we need to set it correctly.
           For some unknown reason, Skia is generating the SVG with a wrong value for the font-weight attribute.
        """
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        root = ET.fromstring(svg)
        elements = root.findall(".//{http://www.w3.org/2000/svg}text")
        for tf in typefaces:
            is_variable_font = tf.typeface.getVariationDesignParameters()
            font_family = self._get_svg_family_name(tf.typeface)
            for text_elem in elements:
                if text_elem.attrib.get("font-family", None) != font_family:
                    continue

                if is_variable_font:
                    # We fix the font-weight if it's present on variable fonts
                    font_weight = text_elem.attrib.get("font-weight", None)
                    if font_weight is not None:
                        text_elem.attrib["font-weight"] = str(tf.typeface.fontStyle().weight())
                else:
                    # We remove the attributes in static fonts
                    text_elem.attrib.pop("font-style", None)
                    text_elem.attrib.pop("font-weight", None)

        return ET.tostring(root, encoding="unicode")

    def _add_shadows(self, svg: str, style: Style):
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        root = ET.fromstring(svg)

        filter = self._build_shadow_svg_filter(root, style.shadows, "text-shadow")
        if filter:
            for text_element in root.findall(".//{http://www.w3.org/2000/svg}text"):
                text_element.set("filter", filter)

        filter = self._build_shadow_svg_filter(root, style.box_shadows, "box-shadow")
        if filter:
            background = self._get_background_element(root)
            if background is not None:
                background.set("filter", filter)

        return ET.tostring(root, encoding="unicode")

    def _build_shadow_svg_filter(self, root: ET.Element, shadows: list[Shadow], prefix: str) -> Optional[str]:
        if not shadows:
            return None

        defs_element = ET.Element("defs")
        root.insert(0, defs_element)

        filter_urls = []
        for i, shadow in enumerate(shadows):
            filter_id = f"{prefix}-{i}"
            filter_urls.append(f"url(#{filter_id})")

            filter_element = ET.Element("filter", {
                "id": filter_id,
                "x": "-50%", "y": "-50%", "width": "200%", "height": "200%"
            })

            ET.SubElement(filter_element, "feOffset", {
                "dx": str(shadow.offset[0]),
                "dy": str(shadow.offset[1]),
                "in": "SourceAlpha",
                "result": "offset"
            })

            input_for_composite = "offset"
            if hasattr(shadow, 'blur_radius') and shadow.blur_radius > 0:
                ET.SubElement(filter_element, "feGaussianBlur", {
                    "in": "offset",
                    "stdDeviation": str(shadow.blur_radius),
                    "result": "blurred"
                })
                input_for_composite = "blurred"

            shadow_color = f"#{shadow.color.r:02x}{shadow.color.g:02x}{shadow.color.b:02x}"
            shadow_opacity = str(shadow.color.a / 255.0)
            ET.SubElement(filter_element, "feFlood", {
                "flood-color": shadow_color,
                "flood-opacity": shadow_opacity,
                "result": "color"
            })

            ET.SubElement(filter_element, "feComposite", {
                "in": "color",
                "in2": input_for_composite,
                "operator": "in",
                "result": "shadow"
            })

            merge_element = ET.SubElement(filter_element, "feMerge")
            ET.SubElement(merge_element, "feMergeNode", {"in": "shadow"})
            ET.SubElement(merge_element, "feMergeNode", {"in": "SourceGraphic"})

            defs_element.append(filter_element)

        return " ".join(filter_urls)

    def _get_background_element(self, root: ET.Element) -> Optional[ET.Element]:
        """
            Skia uses <rect> to represent the background when it doesn't have radius corner
            When it has radius corner, it uses <path> (and a very complex one)
            For this reason, we can't be sure what element is the background
            The fix we decided to use an invisible <rect> that Skia is always generating before the background
            This is something fragile, but it's the fix for now.
            Another fix could be adding a custom invisible marker element before drawing the background,
            then we would use that element to find the background.
        """

        first_rect = root.find("{http://www.w3.org/2000/svg}rect")
        if first_rect is None:
            return None

        siblings = list(root)
        first_rect_index = siblings.index(first_rect)
        if first_rect_index + 1 < len(siblings):
            return siblings[first_rect_index + 1]

        return None
