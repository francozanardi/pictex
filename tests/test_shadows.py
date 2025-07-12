# tests/test_shadows.py

import pytest
from pathlib import Path
from pictex import Canvas
from .utils import check_images_match

def test_render_with_simple_text_shadow(file_regression):
    """
    Tests a single, basic drop shadow on text.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color("white")
        .padding(20)
        .add_shadow(offset=(5, 5), blur_radius=10, color="#000000A0")
    )
    image = canvas.render("Text Shadow")
    check_images_match(file_regression, image)

def test_render_with_simple_box_shadow(file_regression):
    """
    Tests a single, basic drop shadow on the background container.
    """
    canvas = (
        Canvas()
        .font_size(80)
        .color("black")
        .padding(30)
        .background_color("white")
        .background_radius(15)
        .add_box_shadow(offset=(10, 10), blur_radius=20, color="#00000060")
    )
    image = canvas.render("Box Shadow")
    check_images_match(file_regression, image)

def test_render_with_multiple_text_shadows(file_regression):
    """
    Verifies that multiple text shadows can be layered to create complex effects.
    This creates an "engraved" or "inset" look.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .padding(20)
        .background_color("#AAA")
        .color("gray")
        .add_shadow(offset=(3, 3), blur_radius=3, color="black")
        .add_shadow(offset=(-3, -3), blur_radius=0, color="white")
    )
    image = canvas.render("INSET")
    check_images_match(file_regression, image)

def test_render_with_multiple_box_shadows(file_regression):
    """
    Verifies that multiple box shadows can be layered, for example, to create
    a soft outer glow combined with a harder drop shadow.
    """
    canvas = (
        Canvas()
        .font_size(80)
        .padding(40)
        .background_color("white")
        .background_radius(15)
        .add_box_shadow(offset=(5, 5), blur_radius=5, color="#00000040")
        .add_box_shadow(offset=(0, 0), blur_radius=25, color="#3498DB80")
    )
    image = canvas.render("Layered Box")
    check_images_match(file_regression, image)

def test_text_and_box_shadows_together(file_regression):
    """
    Tests the interaction of both text shadows and box shadows on the same element
    to ensure they are both rendered correctly without interference.
    """
    canvas = (
        Canvas()
        .font_size(100)
        .padding(40)
        .background_color("#EEEEEE")
        .background_radius(20)
        .color("#2c3e50")
        .add_shadow(offset=(2, 2), blur_radius=2, color="red")
        .add_box_shadow(offset=(5, 5), blur_radius=3, color="#00000050")
    )
    image = canvas.render("Combined")
    check_images_match(file_regression, image)

def test_hard_shadow_without_blur(file_regression):
    """
    Tests an edge case where blur_radius is zero, creating a hard-edged duplicate.
    This is useful for creating "3D" text effects.
    """
    canvas = (
        Canvas()
        .font_size(120)
        .color("#e74c3c")
        .padding(20)
        .add_shadow(offset=(4, 4), blur_radius=0, color="#2980b9")
        .add_shadow(offset=(8, 8), blur_radius=0, color="#8e44ad")
    )
    image = canvas.render("RETRO")
    check_images_match(file_regression, image)
