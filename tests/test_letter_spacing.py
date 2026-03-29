import pytest
from pictex import Canvas, Column, Text, LetterSpacingMode
from .conftest import STATIC_FONT_PATH, JAPANESE_FONT_PATH


# ---------------------------------------------------------------------------
# Builder API unit tests (no rendering)
# ---------------------------------------------------------------------------

def test_letter_spacing_default_is_normal():
    """The default letter_spacing is LetterSpacing.normal()."""
    text = Text("hello")
    ls = text._style.letter_spacing.get()
    assert ls.is_normal


def test_letter_spacing_pixels_float():
    text = Text("hello").letter_spacing(4.0)
    ls = text._style.letter_spacing.get()
    assert ls.mode == LetterSpacingMode.ABSOLUTE
    assert ls.value == 4.0


def test_letter_spacing_pixels_int():
    text = Text("hello").letter_spacing(4)
    ls = text._style.letter_spacing.get()
    assert ls.mode == LetterSpacingMode.ABSOLUTE
    assert ls.value == 4.0


def test_letter_spacing_negative_pixels():
    text = Text("hello").letter_spacing(-2.5)
    ls = text._style.letter_spacing.get()
    assert ls.mode == LetterSpacingMode.ABSOLUTE
    assert ls.value == -2.5


def test_letter_spacing_percent_string():
    text = Text("hello").letter_spacing("10%")
    ls = text._style.letter_spacing.get()
    assert ls.mode == LetterSpacingMode.PERCENT
    assert ls.value == 10.0


def test_letter_spacing_negative_percent_string():
    text = Text("hello").letter_spacing("-5%")
    ls = text._style.letter_spacing.get()
    assert ls.mode == LetterSpacingMode.PERCENT
    assert ls.value == -5.0


def test_letter_spacing_normal_string():
    """Passing "normal" explicitly resets to the default."""
    text = Text("hello").letter_spacing(8).letter_spacing("normal")
    ls = text._style.letter_spacing.get()
    assert ls.is_normal


def test_letter_spacing_invalid_string_raises():
    with pytest.raises(ValueError):
        Text("hello").letter_spacing("wide")


def test_letter_spacing_is_marked_as_set():
    text = Text("hello").letter_spacing(4)
    assert text._style.is_explicit("letter_spacing")


def test_letter_spacing_is_inheritable():
    text = Text("hello")
    assert text._style.is_inheritable("letter_spacing")


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def test_letter_spacing_percent(file_regression, render_engine):
    """Percentage-based letter spacing relative to space-character width."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(60)
        .background_color("white")
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, Text("Hello, World!").letter_spacing("50%"))
    check_func(file_regression, image)


def test_letter_spacing_comparison(file_regression, render_engine):
    """
    Renders four variants side by side for visual comparison:
    normal, small positive, large positive, negative.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(50)
        .background_color("white")
        .padding(20)
    )
    content = Column(
        Text("normal spacing").background_color("#f0f0f0"),
        Text("spacing +4px").letter_spacing(4).background_color("#f0f0f0"),
        Text("spacing +12px").letter_spacing(12).background_color("#f0f0f0"),
        Text("spacing -3px").letter_spacing(-3).background_color("#f0f0f0"),
    ).gap(10)
    render_func, check_func = render_engine
    image = render_func(canvas, content)
    check_func(file_regression, image)


def test_letter_spacing_override_inheritance(file_regression, render_engine):
    """
    A child Text node can override the inherited letter_spacing.
    """
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(50)
        .background_color("white")
        .padding(20)
        .letter_spacing(8)
    )
    content = Column(
        Text("inherits +8px"),
        Text("overrides to +2px").letter_spacing(2),
        Text("overrides to normal").letter_spacing("normal"),
    ).gap(10)
    render_func, check_func = render_engine
    image = render_func(canvas, content)
    check_func(file_regression, image)


def test_letter_spacing_multiline(file_regression, render_engine):
    """Letter spacing applies consistently across all lines of multi-line text."""
    canvas = (
        Canvas()
        .font_family("Arial")
        .font_size(50)
        .background_color("white")
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, Text("Line one\nLine two\nLine three").letter_spacing(5))
    check_func(file_regression, image)


def test_letter_spacing_with_multirun_text(file_regression, render_engine):
    """
    Letter spacing is applied per-run when text requires font fallbacks
    (e.g. mixed Latin + Japanese characters).
    """
    canvas = (
        Canvas()
        .font_family(STATIC_FONT_PATH)
        .font_fallbacks(JAPANESE_FONT_PATH)
        .font_size(50)
        .background_color("white")
        .padding(20)
    )
    render_func, check_func = render_engine
    image = render_func(canvas, Text("Hello 日本語").letter_spacing(6))
    check_func(file_regression, image)
