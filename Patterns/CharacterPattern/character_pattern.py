"""
SYNOPSIS
    Prints an ASCII-art pattern shaped like any single character you give
    it - letter, digit, or symbol. --char R prints an R-shaped pattern,
    --char O prints an O-shaped pattern, --char 1 prints a 1-shaped
    pattern, and so on for any character your system's font supports.
    Works by rendering the character with a real bold font, cropping to
    its exact ink (so it fills the whole grid regardless of font padding),
    then downsampling the pixels into a text grid of "*" and spaces.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Change FONT_CANDIDATES if arialbd.ttf/arial.ttf aren't on your system

EXAMPLE
    python character_pattern.py --char R
    python character_pattern.py --char N --size 24
    python character_pattern.py --char 1

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import sys

#region Module Dependency Check
REQUIRED_MODULES = ["PIL"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install pillow")
        sys.exit(1)

from PIL import Image, ImageDraw, ImageFont
#endregion

FONT_CANDIDATES = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]
CANVAS_SIZE = 200  # render large, then crop+downsample - keeps the shape crisp regardless of --size


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--char", required=True, help="A single character to render, e.g. R, O, 1")
    parser.add_argument("--size", type=int, default=20, help="Output grid width/height in characters")
    return parser.parse_args()


def load_font(pixel_size):
    for font_path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, pixel_size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_character_grid(char, size):
    if len(char) != 1:
        raise ValueError(f"--char must be exactly one character, got {char!r}")

    image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), color=0)  # black background
    draw = ImageDraw.Draw(image)
    font = load_font(int(CANVAS_SIZE * 0.9))

    bbox = draw.textbbox((0, 0), char, font=font)
    ink_width = bbox[2] - bbox[0]
    ink_height = bbox[3] - bbox[1]
    if ink_width <= 0 or ink_height <= 0:
        raise ValueError(f"Nothing to render for {char!r} - this font may not support that character")

    draw.text((-bbox[0], -bbox[1]), char, fill=255, font=font)
    cropped = image.crop((0, 0, ink_width, ink_height))
    small = cropped.resize((size, size), Image.LANCZOS)
    pixels = small.load()

    lines = []
    for y in range(size):
        row = "".join("*" if pixels[x, y] > 128 else " " for x in range(size))
        lines.append(row)
    return lines


def main():
    args = parse_args()
    try:
        for line in render_character_grid(args.char, args.size):
            print(line)
    except ValueError as ex:
        print(f"Error: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
