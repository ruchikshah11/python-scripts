# Lesson 9: Operators

Reference and demo script covering all of Python's operators.

## Topics
- **Arithmetic** — `+ - * / // % **`, unary `-`
- **Comparison** — `== != > < >= <=`, and Python's chained comparisons (`1 < 2 < 3`)
- **Logical** — `and`, `or`, `not`, and short-circuit evaluation
- **Bitwise** — `& | ^ ~ << >>` (operate on the binary representation of integers)
- **Assignment** — `=` and every augmented form (`+= -= *= /= //= **= %= &= |= ^= <<= >>=`), plus the walrus operator `:=` (3.8+, assign-and-return in one expression)
- **Identity** — `is` / `is not` (compares object identity, not value — contrasted with `==`)
- **Membership** — `in` / `not in` (works on lists, strings, and other collections)
- **Precedence** — quick reminder of evaluation order, right-associativity of `**`, and why parentheses win when unsure

## Run it
```
python operators.py
```

## Exercise
At the bottom of `operators.py`:
1. Compute a total price with `*`, then use `//`/`%` to break it into "$10 notes" + remainder
2. Use `|=` to set two bits in a `flags` variable, then `&` to check a third bit
3. Compare `a is b`, `a is c`, and `a == c` for `a = [1, 2]`, `b = a`, `c = [1, 2]` — and be able to explain the results
4. Use the walrus operator (`:=`) to stop a loop once a running total exceeds 30

## Status
- [ ] Exercise completed
