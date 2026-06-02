# Exercise: Count Word Frequencies

Given a block of text on standard input, count how many times each word appears and print the top-N most frequent words in descending order of frequency.

## Input Format

- Line 1: an integer `N` (1 ≤ N ≤ 100).
- Remaining lines: the text body.

Words are separated by whitespace. Treat words case-insensitively and strip punctuation (`.`, `,`, `!`, `?`, `;`, `:`) from the start and end of each word. Ignore empty tokens.

If two words have the same frequency, sort them alphabetically ascending as a tiebreaker.

## Output Format

Print exactly N lines (or fewer if there are fewer distinct words), each:

```
<word> <count>
```

## Example

Input:
```
3
Go is great. Go is fast. Go goroutines!
```

Output:
```
go 3
is 2
fast 1
```
