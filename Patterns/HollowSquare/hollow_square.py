"""
SYNOPSIS
    Prints a hollow square outline of stars (border only, blank interior),
    sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python hollow_square.py
    python hollow_square.py --rows 7

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


def print_hollow_square(rows):
    for i in range(rows):
        if i == 0 or i == rows - 1:
            print("*" * rows)
        else:
            print("*" + " " * (rows - 2) + "*")


def main():
    args = parse_args()
    print_hollow_square(args.rows)


if __name__ == "__main__":
    main()
