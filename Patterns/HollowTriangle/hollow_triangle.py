"""
SYNOPSIS
    Prints a hollow left-aligned right triangle outline of stars (edges
    only, solid base), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python hollow_triangle.py
    python hollow_triangle.py --rows 7

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


def print_hollow_triangle(rows):
    for i in range(1, rows + 1):
        if i == 1:
            print("*")
        elif i == rows:
            print("*" * i)
        else:
            print("*" + " " * (i - 2) + "*")


def main():
    args = parse_args()
    print_hollow_triangle(args.rows)


if __name__ == "__main__":
    main()
