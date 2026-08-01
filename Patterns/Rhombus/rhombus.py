"""
SYNOPSIS
    Prints a rhombus (slanted square/parallelogram) of stars, sized by
    --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python rhombus.py
    python rhombus.py --rows 7

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


def print_rhombus(rows):
    for i in range(rows):
        print(" " * (rows - i - 1) + "*" * rows)


def main():
    args = parse_args()
    print_rhombus(args.rows)


if __name__ == "__main__":
    main()
