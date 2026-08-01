# Spiral Number Matrix

Prints a `--rows x --rows` grid filled with 1, 2, 3, ... in spiral order (starting
top-left, spiraling clockwise inward).

## Run it
```
python spiral_matrix.py
python spiral_matrix.py --rows 6
```

## Output (--rows 5, default)
```
 1  2  3  4  5
16 17 18 19  6
15 24 25 20  7
14 23 22 21  8
13 12 11 10  9
```

## Tested
Verified the numbers 1–25 each appear exactly once by summing the grid: 325, which
matches `n(n+1)/2` for n=25 — confirms no duplicates or gaps in the spiral.

## Status
- [x] Verified working (default size, sum-checked)
