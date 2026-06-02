# Word Frequency Counter

Read text from standard input. The first line is an integer `N`. The remaining lines form the text body.

Count word occurrences case-insensitively, stripping leading/trailing punctuation (`.`, `,`, `!`, `?`, `;`, `:`) from each token. Print the top `N` most frequent words (descending frequency; alphabetical tiebreak), one per line as `<word> <count>`.

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
