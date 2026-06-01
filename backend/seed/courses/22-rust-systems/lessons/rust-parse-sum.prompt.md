# Parse and Sum

Read whitespace-separated tokens from stdin. If every token parses as an integer, print the sum. On the **first** non-integer token, print `ERROR <token>` and stop (don't sum the remaining).

## Input

Any number of tokens separated by whitespace (spaces or newlines).

## Output

- The integer sum (one line), OR
- `ERROR <token>` for the first token that fails to parse.

If the input has no tokens, print `0`.

## Examples

Input: `1 2 3 4` → Output: `10`

Input: `1 2 abc 4` → Output: `ERROR abc`

Input: `-5 5 -10 10` → Output: `0`

Input: (empty) → Output: `0`

## Notes

- Negative integers must parse correctly.
- Stop at the first error — don't keep summing valid tokens after it.
- Token whitespace handling: split by any whitespace, ignore empty results.
