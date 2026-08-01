"""
SYNOPSIS
    Prints a plus/cross (+) sign made of stars in a (2*rows-1) x (2*rows-1)
    grid, sized by --rows (half-width from the center).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python plus_pattern.py
    python plus_pattern.py --rows 7

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


def print_plus(rows):
    size = 2 * rows - 1
    middle = rows - 1
    for i in range(size):
        print("".join("*" if (i == middle or j == middle) else " " for j in range(size)))


def main():
    args = parse_args()
    print_plus(args.rows)


if __name__ == "__main__":
    main()
