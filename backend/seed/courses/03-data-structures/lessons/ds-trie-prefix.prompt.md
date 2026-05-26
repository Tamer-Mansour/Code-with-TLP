# Trie Prefix Search

Given a dictionary of words and a list of queries, for each query determine whether it is:

- `WORD` — an exact word in the dictionary,
- `PREFIX` — a prefix of at least one word in the dictionary (but not an exact word itself), or
- `NONE` — neither.

## Input Format

- Line 1: integer `n` — number of dictionary words.
- Next `n` lines: one word per line (lowercase letters only).
- Next line: integer `q` — number of queries.
- Next `q` lines: one query string per line.

## Output Format

For each query print `WORD`, `PREFIX`, or `NONE` on its own line.

## Constraints

- `1 <= n, q <= 500`
- Words and queries contain only lowercase letters, length 1–20.

## Examples

**Example 1**
```
Input:
4
cat
car
card
bat
3
cat
ca
dog

Output:
WORD
PREFIX
NONE
```

**Example 2**
```
Input:
2
hello
world
2
hell
hello

Output:
PREFIX
WORD
```
