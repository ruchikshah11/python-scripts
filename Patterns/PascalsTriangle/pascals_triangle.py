"""
SYNOPSIS
    Prints Pascal's Triangle (each number is the sum of the two above it),
    centered, sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console. Uses
    math.comb(row, k) directly rather than building each row from the
    previous one, since it's simpler and just as correct for this size.

EXAMPLE
    python pascals_triangle.py
    python pascals_triangle.py --rows 7

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import math


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5)
    return parser.parse_args()


def print_pascals_triangle(rows):
    all_rows = [[math.comb(row, k) for k in range(row + 1)] for row in range(rows)]
    lines = [" ".join(str(value) for value in row) for row in all_rows]
    width = len(lines[-1])

    for line in lines:
        print(line.center(width))


def main():
    args = parse_args()
    print_pascals_triangle(args.rows)


if __name__ == "__main__":
    main()
