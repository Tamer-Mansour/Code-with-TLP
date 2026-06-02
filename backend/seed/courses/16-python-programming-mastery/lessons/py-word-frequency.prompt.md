# Word Frequency Counter

Read a single line of text from standard input. Count how many times each unique word appears (treat the text as **case-insensitive** and strip leading/trailing punctuation from each token using `str.strip` with `string.punctuation`).

Print each `word: count` pair on its own line, sorted **alphabetically** by the lowercase word.

## Constraints

- Input is a single line; words are separated by whitespace.
- Comparisons and output are lowercase.
- Strip punctuation characters from the start and end of each token only (do not split on punctuation inside a word like "don't").
- Use only the Python standard library.

## Example

**Input:**
```
Hello, world! Hello Python... world world
```

**Output:**
```
hello: 2
python: 1
world: 3
```
