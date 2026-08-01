"""
SYNOPSIS
    Prints a left-aligned inverted right triangle of stars (--rows stars
    shrinking to 1 star), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python inverted_triangle.py
    python inverted_triangle.py --rows 7

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


def print_inverted_triangle(rows):
    for i in range(rows, 0, -1):
        print("*" * i)


def main():
    args = parse_args()
    print_inverted_triangle(args.rows)


if __name__ == "__main__":
    main()
