"""
SYNOPSIS
    Prints a centered palindromic number pyramid (1 / 121 / 12321 / ...),
    sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python palindromic_pattern.py
    python palindromic_pattern.py --rows 7

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


def print_palindromic_pattern(rows):
    width = 2 * rows - 1
    for i in range(1, rows + 1):
        ascending = "".join(str(n % 10) for n in range(1, i + 1))
        descending = "".join(str(n % 10) for n in range(i - 1, 0, -1))
        print((ascending + descending).center(width))


def main():
    args = parse_args()
    print_palindromic_pattern(args.rows)


if __name__ == "__main__":
    main()
