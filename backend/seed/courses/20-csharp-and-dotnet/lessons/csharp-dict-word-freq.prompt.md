# Dictionary Word Frequency

Read a single line of **space-separated words** from stdin.

Count how many times each unique word appears (treat the comparison as **case-insensitive** — convert all words to lowercase before counting).

Print each word and its count in **alphabetical order**, formatted as `<word>: <count>`.

## Input

A single line of one or more words separated by spaces.

## Output

One line per unique word (lowercase), in alphabetical order: `<word>: <count>`.

## Example

**Input:**
```
the quick brown fox jumps over the lazy dog the fox
```

**Output:**
```
brown: 1
dog: 1
fox: 2
jumps: 1
lazy: 1
over: 1
quick: 1
the: 3
```
