"""
SYNOPSIS
    Prints Floyd's Triangle - sequential numbers filling a triangle, row i
    has i numbers, counting continues across rows, sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python floyds_triangle.py
    python floyds_triangle.py --rows 7

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


def print_floyds_triangle(rows):
    counter = 1
    for i in range(1, rows + 1):
        row_numbers = []
        for _ in range(i):
            row_numbers.append(str(counter))
            counter += 1
        print(" ".join(row_numbers))


def main():
    args = parse_args()
    print_floyds_triangle(args.rows)


if __name__ == "__main__":
    main()
