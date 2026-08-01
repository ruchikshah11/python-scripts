"""
SYNOPSIS
    Prints a number pyramid - row i repeats the digit i, i times
    (1 / 22 / 333 / ...), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python number_pyramid.py
    python number_pyramid.py --rows 7

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


def print_number_pyramid(rows):
    for i in range(1, rows + 1):
        print(str(i % 10) * i)


def main():
    args = parse_args()
    print_number_pyramid(args.rows)


if __name__ == "__main__":
    main()
