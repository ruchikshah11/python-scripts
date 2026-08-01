"""
SYNOPSIS
    Prints a number triangle - row i contains the digits 1 through i
    concatenated (1 / 12 / 123 / ...), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python number_triangle.py
    python number_triangle.py --rows 7

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


def print_number_triangle(rows):
    for i in range(1, rows + 1):
        print("".join(str(n % 10) for n in range(1, i + 1)))


def main():
    args = parse_args()
    print_number_triangle(args.rows)


if __name__ == "__main__":
    main()
