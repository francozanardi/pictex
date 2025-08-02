from typing import Optional
from ..models import TypefaceLoadingInfo, TypefaceSource
import skia

class TypefaceLoader:
    _typefaces_loading_info: list[TypefaceLoadingInfo] = []
    _font_manager: skia.FontMgr = None

    @staticmethod
    def load_default() -> skia.Typeface:
        return TypefaceLoader._save(skia.Typeface.MakeDefault(), TypefaceSource.SYSTEM)

    @staticmethod
    def load_from_file(filepath: str) -> Optional[skia.Typeface]:
        return TypefaceLoader._save(skia.Typeface.MakeFromFile(filepath), TypefaceSource.FILE, filepath)

    @staticmethod
    def load_system_font(family: str, style: skia.FontStyle = None) -> skia.Typeface:
        """
            Creates a new reference to the typeface that most closely
            matches the requested familyName and fontStyle.
            Will never return null.
        """
        return TypefaceLoader._save(skia.Typeface(family, style), TypefaceSource.SYSTEM)

    @staticmethod
    def load_for_glyph(glyph: str, style: skia.FontStyle) -> Optional[skia.Typeface]:
        system_typeface = TypefaceLoader._get_font_manager().matchFamilyStyleCharacter(
            "",
            style,
            [],
            ord(glyph)
        )
        return TypefaceLoader._save(system_typeface, TypefaceSource.SYSTEM)

    @staticmethod
    def clone_with_arguments(typeface: skia.Typeface, arguments: skia.FontArguments) -> skia.Typeface:
        typeface_loading_info = TypefaceLoader.get_typeface_loading_info(typeface)
        if not typeface_loading_info:
            raise RuntimeError("Impossible to clone typeface: it was not loaded")

        new_typeface = typeface.makeClone(arguments)
        typeface_loading_info.typeface = new_typeface
        return new_typeface
    
    @staticmethod
    def get_typeface_loading_info(typeface: skia.Typeface) -> Optional[TypefaceLoadingInfo]:
        for loading_info in TypefaceLoader._typefaces_loading_info:
            if loading_info.typeface == typeface:
                return loading_info
        return None

    @staticmethod
    def _save(typeface: Optional[skia.Typeface], source: TypefaceSource, filepath: Optional[str] = None) -> Optional[skia.Typeface]:
        if not typeface:
            return None
        
        TypefaceLoader._typefaces_loading_info.append(TypefaceLoadingInfo(typeface, source, filepath))
        return typeface

    @staticmethod
    def _get_font_manager() -> skia.FontMgr:
        if TypefaceLoader._font_manager is None:
            TypefaceLoader._font_manager = skia.FontMgr()
        return TypefaceLoader._font_manager
