# Word Frequency Counter

Read lines from standard input until **EOF**.

Count how many times each word appears. Words are **case-insensitive** and you should consider only **alphanumeric characters** — strip any punctuation by keeping only characters for which `c.isalnum()` returns `True`.

Print each unique word and its count in **alphabetical order**, one per line in the format:

```
word: count
```

## Input format

Multiple lines of text (terminated by EOF). Each line may contain one or more words separated by whitespace.

## Output format

One line per unique word (after normalisation), sorted alphabetically, in the format `word: count`.

## Example

**Input:**
```
Hello world
hello Python
world is great
```

**Output:**
```
great: 1
hello: 2
is: 1
python: 1
world: 2
```

## Notes

- `"Hello"` and `"hello"` are the same word (both become `"hello"`).
- Punctuation is stripped: `"world!"` becomes `"world"`.
- Empty strings after stripping should be ignored.
- Output is in ascending alphabetical order.
