# Top-N Word Count

Read an integer K on the first line, then a body of text on the remaining lines. Print the K most common words in the text, sorted by **count descending**, ties broken **alphabetically ascending**.

## Input

```
K
<line 1>
<line 2>
...
```

- `K` is the number of top words to keep (1 ≤ K ≤ 1000).
- The remaining lines together form the text. Words are separated by whitespace (any combination of spaces and newlines).
- Words are compared **case-sensitively** as given.

## Output

K lines (or fewer if fewer unique words exist), each `word count` separated by one space, ordered by count desc then word asc.

## Examples

Input:

```
3
the quick brown fox jumps over the lazy dog the
```

Output:

```
the 3
brown 1
dog 1
```

Input:

```
2
b a a b c
```

Output:

```
a 2
b 2
```

## Notes

- Whitespace-only input or `K = 0` should produce no output.
- No punctuation handling — split purely on whitespace.
