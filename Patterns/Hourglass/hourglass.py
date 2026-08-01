"""
SYNOPSIS
    Prints an hourglass pattern of stars (a solid inverted pyramid on top of
    a solid pyramid - the opposite of Diamond), sized by --rows (half-height).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python hourglass.py
    python hourglass.py --rows 7

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


def print_hourglass(rows):
    for i in range(rows, 0, -1):
        print(" " * (rows - i) + "*" * (2 * i - 1))
    for i in range(2, rows + 1):
        print(" " * (rows - i) + "*" * (2 * i - 1))


def main():
    args = parse_args()
    print_hourglass(args.rows)


if __name__ == "__main__":
    main()
