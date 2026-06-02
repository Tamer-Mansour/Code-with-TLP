# Exercise: Word Frequency Counter

In this exercise you will simulate a classic Rust HashMap pattern: counting word occurrences in a body of text.

Given a line of space-separated words on stdin, print each unique word and its count, one per line, sorted alphabetically. Words are case-sensitive.

## Example

Input:
```
the quick brown fox jumps over the lazy dog the fox
```

Output:
```
brown 1
dog 1
fox 2
jumps 1
lazy 1
over 1
quick 1
the 3
```

This mirrors the `entry().or_insert()` pattern you learned in the Collections lesson — a fundamental Rust idiom.
