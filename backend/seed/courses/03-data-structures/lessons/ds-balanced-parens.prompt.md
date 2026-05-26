# Balanced Parentheses

Given a string containing only the characters `(`, `)`, `{`, `}`, `[`, and `]`, determine whether the brackets are balanced.

A string is balanced if:
1. Every opening bracket has a matching closing bracket of the same type.
2. Brackets are closed in the correct order (most-recently opened closes first).

## Input Format

- Line 1: a single integer `t` — the number of test strings.
- The next `t` lines: one string per line (may contain only bracket characters, no spaces).

## Output Format

For each test string print `YES` if balanced, `NO` otherwise, one result per line.

## Constraints

- `1 <= t <= 100`
- `0 <= len(string) <= 1000`

## Examples

**Example 1**
```
Input:
4
()
()[{}]
(]
([)]

Output:
YES
YES
NO
NO
```
