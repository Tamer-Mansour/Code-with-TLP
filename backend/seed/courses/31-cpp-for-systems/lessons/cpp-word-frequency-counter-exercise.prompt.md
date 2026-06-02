# Prompt: Word Frequency Counter

## Problem Description

Read lines of text from standard input. Count the frequency of each word (case-insensitive, punctuation-stripped) and print the results sorted alphabetically.

## Input Format

- Zero or more lines of text, each containing space-separated tokens.
- Input ends at EOF.
- Lines may be empty.

## Output Format

- One line per unique word: `<word> <count>`
- Words are printed in **ascending alphabetical order**.
- Word and count are separated by a single space.
- No trailing spaces.
- If the input contains no words, produce no output.

## Normalisation Rules

1. Convert all letters to lowercase.
2. Strip leading and trailing punctuation characters from the token. Punctuation characters are: `. , ! ? ' " ; :`
3. If the token is empty after stripping, skip it.
4. Do not strip punctuation from the interior of a word (e.g., `"don't"` → `"don't"`).

## Constraints

- Total input length: at most 100 000 characters.
- Tokens per line: at most 1 000.
- Each token (before normalisation) is at most 100 characters.
- All characters are printable ASCII.

## Sample Input 1

```
hello world
Hello again world
```

## Sample Output 1

```
again 1
hello 2
world 2
```

## Sample Input 2

```
To be, or not to be: that is the question.
```

## Sample Output 2

```
be 2
is 1
not 1
or 1
question 1
that 1
the 1
to 2
```

## Sample Input 3

```
One! one, ONE.
```

## Sample Output 3

```
one 3
```

## Sample Input 4 (empty input)

```

```

## Sample Output 4

```
```

(no output)

## Notes for Implementers

- Split only on space characters (ASCII 0x20); do not split on tabs or other whitespace unless they appear as spaces.
- The stripping of punctuation applies to the *boundaries* of each token only. Interior characters are preserved.
- Frequency counting via `map[word]++` is the idiomatic C++ approach; a Python `dict` or `collections.Counter` is equally valid.
