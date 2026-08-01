"""
SYNOPSIS
    Prints an alphabet triangle - row i contains letters A through the i-th
    letter concatenated (A / AB / ABC / ...), sized by --rows.

DESCRIPTION
    Run this file to see the pattern printed to the console.

EXAMPLE
    python alphabet_triangle.py
    python alphabet_triangle.py --rows 7

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


def print_alphabet_triangle(rows):
    for i in range(1, rows + 1):
        print("".join(chr(ord("A") + j) for j in range(i)))


def main():
    args = parse_args()
    print_alphabet_triangle(args.rows)


if __name__ == "__main__":
    main()
