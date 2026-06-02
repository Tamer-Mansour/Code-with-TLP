# Word Frequency Counter

Read lines of text from standard input. Count how many times each word appears (case-insensitive). A word is a sequence of non-whitespace characters. Output each unique word (lowercase) and its count, one per line, sorted by count descending. Break ties alphabetically (ascending).

## Input

Multiple lines of space-separated words. No punctuation stripping required — treat each whitespace-delimited token as a word.

## Output

Lines of the form `<word> <count>`, sorted by count descending, ties broken alphabetically.

## Example

Input:
```
hello world hello
world hello
```

Output:
```
hello 3
world 2
```
