class FontNotFoundWarning(Warning):
    """
        Warning raised when a user defined font is not found.
        Either a system font or a font file.

        PicTex will continue the execution with the next fallback font if defined,
        otherwise the default system font will be used.
    """
    pass

class SystemFontCanNotBeEmbeddedInSvgWarning(Warning):
    """
        Warning raised when a user render a image as svg,
        with the flag `embed_fonts = True`, but system fonts are being used.

        The system fonts can't be embedded in a SVG file.
        PicTex will continue the execution are ignore the system fonts in the final SVG.
    """
