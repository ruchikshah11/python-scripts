"""
SYNOPSIS
    Prints a butterfly pattern (two triangles mirrored side by side,
    widening then narrowing), sized by --rows (half-height).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python butterfly_pattern.py
    python butterfly_pattern.py --rows 7

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


def print_butterfly(rows):
    for i in range(1, rows + 1):
        print("*" * i + " " * (2 * (rows - i)) + "*" * i)
    for i in range(rows, 0, -1):
        print("*" * i + " " * (2 * (rows - i)) + "*" * i)


def main():
    args = parse_args()
    print_butterfly(args.rows)


if __name__ == "__main__":
    main()
