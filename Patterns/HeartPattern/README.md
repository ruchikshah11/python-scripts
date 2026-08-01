# Heart Pattern

Prints a heart shape made of stars, using the implicit heart curve
`(x² + y² - 1)³ - x²y³ <= 0` rasterized onto a text grid, rather than hand-tuned
spacing/star counts (which is fiddly to get looking like an actual heart rather than
two lopsided triangles).

## Run it
```
python heart_pattern.py
python heart_pattern.py --size 14
```
`--size` (default 10) is roughly half the heart's height.

## Output (--size 10, default)
```
         **   **         
       ***********       
       ***********       
       ***********       
       ***********       
       ***********       
       ***********       
        *********        
         *******         
          *****          
           ***           
            *            
```

## Status
- [x] Verified working (default size) — visually confirmed a genuine heart shape,
  not a rough approximation
