class FontNotFoundWarning(Warning):
    """
        Warning raised when a user defined font is not found.
        Either a system font or a font file.

        PicTex will continue the execution with the next fallback font if defined,
        otherwise the default system font will be used.
    """
    pass
