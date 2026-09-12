# Matrix Addition

Adds two matrices (Matrix A is RowsA x ColsA, Matrix B is RowsB x ColsB - both
dimensions must match exactly for addition) element-wise
(`C[i][j] = A[i][j] + B[i][j]`) and prints Matrix A, Matrix B, and the sum. Pure
standard library.

**By default, prompts for every cell of both matrices one at a time** (Matrix A first,
then Matrix B), with a "please enter a whole number" retry on invalid input. Pass
`--random` to generate random integers instead - useful for a quick demo without
typing in every value.

This is the Python port of the PowerShell version (`Invoke-MatrixAddition.ps1`, in the
`Utilities/Algorithms/Matrix` folder of the `powershell-scripts` repo) - keep both in
sync if the algorithm changes. Sibling to
[MatrixMultiplication](../MatrixMultiplication/README.md), same conventions.

## Prerequisites
None beyond the standard library.

## Run it
```
# Prompts for every cell of two 2x3 matrices
python matrix_addition.py --rows-a 2 --cols-a 3 --rows-b 2 --cols-b 3

# Random matrices instead of prompting, reproducible via --seed
python matrix_addition.py --rows-a 3 --cols-a 3 --rows-b 3 --cols-b 3 --random --seed 42
python matrix_addition.py --rows-a 4 --cols-a 4 --rows-b 4 --cols-b 4 --random --min -5 --max 5
```
Both matrices must have identical dimensions - a clear error is printed otherwise, not
a crash.

## Complexity
O(Rows * Cols).

## Tested
- `--rows-a 2 --cols-a 3 --rows-b 2 --cols-b 3 --random --seed 5`: manually verified
  every result cell by hand - correct.
- Manual entry mode (piped stdin): entered two 2x2 matrices cell-by-cell, verified the
  sum (11/22/33/44) by hand - correct.
- Mismatched dimensions (`--rows-a 2 --cols-a 3 --rows-b 3 --cols-b 2`): fails with a
  clear error message, not a crash or a silently wrong result.

## Logging
Logs are written to `Logs/matrix_addition_<date>.log`, with a per-run CorrelationID
and 7-day retention - same pattern as
[ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working: correct sums (hand-checked), manual cell-by-cell entry, random
  mode, and dimension-mismatch handling all confirmed correct.
