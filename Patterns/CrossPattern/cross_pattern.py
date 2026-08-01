"""
SYNOPSIS
    Prints an X (cross) sign made of stars in a (2*rows-1) x (2*rows-1)
    grid, sized by --rows (half-width from the center).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python cross_pattern.py
    python cross_pattern.py --rows 7

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


def print_cross(rows):
    size = 2 * rows - 1
    for i in range(size):
        print("".join("*" if (j == i or j == size - 1 - i) else " " for j in range(size)))


def main():
    args = parse_args()
    print_cross(args.rows)


if __name__ == "__main__":
    main()
