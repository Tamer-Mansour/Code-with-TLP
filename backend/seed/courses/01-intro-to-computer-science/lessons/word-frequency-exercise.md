# Word Frequency Counter

This exercise combines string manipulation, dictionary usage, and sorting — the three pillars of text processing in Python.

## What You Will Practice

- Iterating over `sys.stdin` to read until EOF
- String normalisation: `lower()` and character filtering with `isalnum()`
- Building a frequency map with a dictionary
- Sorting dictionary keys and printing formatted output

## Approach

1. Read lines until EOF using `for line in sys.stdin`.
2. For each line, split into words with `.split()`.
3. Normalise each word: convert to lowercase, keep only alphanumeric characters.
4. Use a dictionary to count: `freq[word] = freq.get(word, 0) + 1`.
5. Print each key-value pair in sorted order.

```python
import sys

freq = {}
for line in sys.stdin:
    for word in line.split():
        cleaned = ''.join(c for c in word if c.isalnum()).lower()
        if cleaned:                        # skip empty strings
            freq[cleaned] = freq.get(cleaned, 0) + 1

for word in sorted(freq):
    print(f'{word}: {freq[word]}')
```

## Why `freq.get(word, 0) + 1`?

`dict.get(key, default)` returns the value for `key` if it exists, or `default` if it does not. This avoids a `KeyError` when encountering a word for the first time, replacing the pattern:

```python
if word in freq:
    freq[word] += 1
else:
    freq[word] = 1
```

with the more concise one-liner shown above.
