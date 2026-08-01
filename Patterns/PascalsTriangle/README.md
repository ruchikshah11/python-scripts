# Pascal's Triangle

Prints Pascal's Triangle (each number is the sum of the two above it), centered,
sized by `--rows`. Uses `math.comb(row, k)` directly rather than building each row
from the previous one.

## Run it
```
python pascals_triangle.py
python pascals_triangle.py --rows 7
```

## Output (--rows 5, default)
```
    1    
   1 1   
  1 2 1  
 1 3 3 1 
1 4 6 4 1
```

## Output (--rows 7)
```
       1        
      1 1       
     1 2 1      
    1 3 3 1     
   1 4 6 4 1    
 1 5 10 10 5 1  
1 6 15 20 15 6 1
```

## Status
- [x] Verified working (default size and `--rows 7`) — binomial coefficients checked
  correct
