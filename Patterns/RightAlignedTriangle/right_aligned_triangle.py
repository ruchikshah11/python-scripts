"""
SYNOPSIS
    Prints a right-aligned right triangle of stars (1 star growing to
    --rows stars, aligned to the right edge), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python right_aligned_triangle.py
    python right_aligned_triangle.py --rows 7

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
    parser.add_argument("--rows", type=int, default=5)
    return parser.parse_args()


def print_right_aligned_triangle(rows):
    for i in range(1, rows + 1):
        print(" " * (rows - i) + "*" * i)


def main():
    args = parse_args()
    print_right_aligned_triangle(args.rows)


if __name__ == "__main__":
    main()
