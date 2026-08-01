"""
SYNOPSIS
    Prints a hollow diamond outline of stars (edges only, blank interior),
    sized by --rows (half-height).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python hollow_diamond.py
    python hollow_diamond.py --rows 7

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse


def print_hollow_half(rows, top_to_bottom):
    row_range = range(1, rows + 1) if top_to_bottom else range(rows - 1, 0, -1)
    for i in row_range:
        if i == 1:
            print(" " * (rows - i) + "*")
        else:
            print(" " * (rows - i) + "*" + " " * (2 * i - 3) + "*")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5)
    return parser.parse_args()


def print_hollow_diamond(rows):
    print_hollow_half(rows, top_to_bottom=True)
    print_hollow_half(rows, top_to_bottom=False)


def main():
    args = parse_args()
    print_hollow_diamond(args.rows)


if __name__ == "__main__":
    main()
