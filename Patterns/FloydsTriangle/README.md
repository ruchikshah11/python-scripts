# Floyd's Triangle

Prints Floyd's Triangle — sequential numbers filling a triangle, row *i* has *i*
numbers, counting continues across rows, sized by `--rows`.

## Run it
```
python floyds_triangle.py
python floyds_triangle.py --rows 7
```

## Output (--rows 5, default)
```
1
2 3
4 5 6
7 8 9 10
11 12 13 14 15
```

## Status
- [x] Verified working (default size) — final number (15) checked correct against
  the triangular number formula n(n+1)/2 for n=5
