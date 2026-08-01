"""
SYNOPSIS
    Prints a solid, centered diamond of stars (a pyramid on top of an
    inverted pyramid), sized by --rows (half-height).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python diamond.py
    python diamond.py --rows 7

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


def print_diamond(rows):
    for i in range(1, rows + 1):
        print(" " * (rows - i) + "*" * (2 * i - 1))
    for i in range(rows - 1, 0, -1):
        print(" " * (rows - i) + "*" * (2 * i - 1))


def main():
    args = parse_args()
    print_diamond(args.rows)


if __name__ == "__main__":
    main()
