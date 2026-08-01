"""
SYNOPSIS
    Prints a checkerboard pattern of stars and spaces, sized by --rows
    (a --rows x --rows grid).

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python checkerboard.py
    python checkerboard.py --rows 8

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


def print_checkerboard(rows):
    for i in range(rows):
        print("".join("*" if (i + j) % 2 == 0 else " " for j in range(rows)))


def main():
    args = parse_args()
    print_checkerboard(args.rows)


if __name__ == "__main__":
    main()
