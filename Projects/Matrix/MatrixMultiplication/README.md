# Matrix Multiplication

Multiplies two matrices (Matrix A is RowsA x ColsA, Matrix B is RowsB x ColsB - not
necessarily square, and not necessarily the same size as each other, as long as
`ColsA == RowsB`) using the classic triple-loop algorithm
(`C[i][j] = sum(A[i][k] * B[k][j] for k in range(ColsA))`) and prints Matrix A, Matrix
B, and the product. Pure standard library - no numpy - so the algorithm itself stays
visible instead of hiding behind a library call.

**By default, prompts for every cell of both matrices one at a time** (Matrix A first,
then Matrix B), with a "please enter a whole number" retry on invalid input. Pass
`--random` to generate random integers instead - useful for a quick demo without
typing in every value.

This is the Python port of the PowerShell version (`Invoke-MatrixMultiplication.ps1`,
in the `Utilities/Algorithms/Matrix` folder of the `powershell-scripts` repo) - keep
both in sync if the algorithm changes.

## Prerequisites
None beyond the standard library.

## Run it
```
# Prompts for every cell of a 2x3 matrix and a 3x2 matrix
python matrix_multiplication.py --rows-a 2 --cols-a 3 --rows-b 3 --cols-b 2

# Random 3x3 matrices instead of prompting, reproducible via --seed
python matrix_multiplication.py --rows-a 3 --cols-a 3 --rows-b 3 --cols-b 3 --random --seed 42
python matrix_multiplication.py --rows-a 4 --cols-a 4 --rows-b 4 --cols-b 4 --random --min -5 --max 5
```
`ColsA` must equal `RowsB` (Matrix A's column count = Matrix B's row count) - a clear
error is printed otherwise, not a crash.

## Complexity
O(RowsA * ColsB * ColsA) - the script logs the actual elapsed multiplication time and
the operation count for whatever dimensions were given.

## Tested
- `--rows-a 2 --cols-a 3 --rows-b 3 --cols-b 2 --random --seed 7`: manually verified
  every result cell by hand (e.g. Result[0][0] = 6*2+3*1+7*4 = 43) - correct.
- Manual entry mode (piped stdin): entered a 2x3 and a 3x2 matrix cell-by-cell,
  verified the product (58/64/139/154) by hand - correct.
- Invalid non-integer input (`abc`): correctly re-prompts with "Please enter a whole
  number." instead of crashing.
- Mismatched dimensions (`--cols-a 3 --rows-b 2`): fails with a clear error message,
  not a crash or a silently wrong result.
- `--rows-a 3 --cols-a 2 --rows-b 2 --cols-b 4`: another non-square case, spot-checked
  by hand - correct.

## Logging
Logs are written to `Logs/matrix_multiplication_<date>.log`, with a per-run
CorrelationID and 7-day retention - same pattern as
[ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working: non-square multiplication, manual cell-by-cell entry with
  input validation, random mode, and dimension-mismatch handling all confirmed correct.
