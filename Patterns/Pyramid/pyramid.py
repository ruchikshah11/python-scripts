"""
SYNOPSIS
    Prints a solid, centered pyramid of stars, sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python pyramid.py
    python pyramid.py --rows 7

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


def print_pyramid(rows):
    for i in range(1, rows + 1):
        print(" " * (rows - i) + "*" * (2 * i - 1))


def main():
    args = parse_args()
    print_pyramid(args.rows)


if __name__ == "__main__":
    main()
