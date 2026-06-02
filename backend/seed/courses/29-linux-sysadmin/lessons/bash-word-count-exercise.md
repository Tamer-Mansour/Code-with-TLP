# Exercise: Word Frequency Counter

Given lines of text on standard input, count how many times each word appears (case-insensitive, split on whitespace). Output one `word count` pair per line, sorted by count descending, then alphabetically for ties.

## Input format

Multiple lines of plain text.

## Output format

One line per word: `<word> <count>`, sorted by count descending. If two words have the same count, sort them alphabetically.

## Example

**Input:**
```
hello world hello
world hello
```

**Output:**
```
hello 3
world 2
```
