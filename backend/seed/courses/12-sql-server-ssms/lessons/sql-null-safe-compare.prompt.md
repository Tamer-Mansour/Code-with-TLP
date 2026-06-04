# NULL-Safe Comparison (Three-Valued Logic)

## Problem

You are given **N** rows, each containing a product name and an optional price. The price field is either a numeric string (e.g., `1.50`) or the literal string `NULL`, which represents a SQL NULL — a missing value.

For each row, print:
- `Priced` if the price is a valid number (not NULL)
- `Unpriced` if the price is `NULL`

Output one label per line, in the same order as the input rows.

This exercises the core SQL rule that NULL must be tested with `IS NULL`, not `= NULL`.

## Input Format

- Line 1: integer `N` — the number of product rows
- Next `N` lines: `product_name,price` where `price` is either a decimal number or the string `NULL`

## Output Format

One line per product: either `Priced` or `Unpriced`, in original order.

## Constraints

- `1 <= N <= 500`
- Product names contain no commas
- Prices, when present, are non-negative decimal numbers

## Example

**Input:**
```
4
Apple,1.50
Banana,NULL
Cherry,2.00
Date,NULL
```

**Output:**
```
Priced
Unpriced
Priced
Unpriced
```

Apple and Cherry have prices, so they are `Priced`. Banana and Date have `NULL` prices, so they are `Unpriced`.
