"""
SYNOPSIS
    Prints a --rows x --rows grid filled with 1, 2, 3, ... in spiral order
    (starting top-left, spiraling clockwise inward).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python spiral_matrix.py
    python spiral_matrix.py --rows 6

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


def build_spiral_matrix(size):
    grid = [[0] * size for _ in range(size)]
    top, bottom, left, right = 0, size - 1, 0, size - 1
    value = 1

    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            grid[top][col] = value
            value += 1
        top += 1

        for row in range(top, bottom + 1):
            grid[row][right] = value
            value += 1
        right -= 1

        if top <= bottom:
            for col in range(right, left - 1, -1):
                grid[bottom][col] = value
                value += 1
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                grid[row][left] = value
                value += 1
            left += 1

    return grid


def print_spiral_matrix(rows):
    grid = build_spiral_matrix(rows)
    width = len(str(rows * rows))
    for row in grid:
        print(" ".join(str(value).rjust(width) for value in row))


def main():
    args = parse_args()
    print_spiral_matrix(args.rows)


if __name__ == "__main__":
    main()
