# Diamond Pattern

Prints a solid, centered diamond of stars (a pyramid on top of an inverted pyramid,
sharing no duplicate middle row), sized by `--rows` (half-height).

## Run it
```
python diamond.py
python diamond.py --rows 7
```

## Output (--rows 5, default)
```
    *
   ***
  *****
 *******
*********
 *******
  *****
   ***
    *
```

## Output (--rows 3)
```
  *
 ***
*****
 ***
  *
```

## Status
- [x] Verified working (default size and `--rows 3`)
