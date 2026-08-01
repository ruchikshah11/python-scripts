"""
SYNOPSIS
    Prints a heart shape made of stars, using the implicit heart curve
    (x^2 + y^2 - 1)^3 - x^2*y^3 <= 0 rasterized onto a text grid, rather
    than hand-tuned spacing/star counts (which is fiddly to get looking
    like an actual heart). Sized by --size (roughly half-height).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python heart_pattern.py
    python heart_pattern.py --size 14

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=10, help="Roughly half the heart's height")
    return parser.parse_args()


def print_heart(size):
    for y in range(size, -size - 1, -1):
        row_chars = []
        for x in range(-size - 2, size + 3):
            x_scaled = x / (size / 2)
            y_scaled = y / (size / 2)
            value = (x_scaled ** 2 + y_scaled ** 2 - 1) ** 3 - (x_scaled ** 2) * (y_scaled ** 3)
            row_chars.append("*" if value <= 0 else " ")
        print("".join(row_chars))


def main():
    args = parse_args()
    print_heart(args.size)


if __name__ == "__main__":
    main()
