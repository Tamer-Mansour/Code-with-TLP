# Run-Length Encoding / Decoding

Read one line from standard input.

- If the line starts with a **letter** (a-z), **encode** it with RLE: replace each run of identical characters with `<count><char>` (e.g., `aaa` → `3a`, single `b` → `1b`).
- If the line starts with a **digit** (0-9), **decode** it: each `<count><char>` pair expands to that character repeated `count` times.

Print the result on a single line.

## Examples

Input: `aaabccddddee` → Output: `3a1b2c4d2e`

Input: `3a1b2c4d2e` → Output: `aaabccddddee`
