# Exercise: Word Frequency Counter (Map Semantics)

In this exercise you will implement a word frequency counter that demonstrates real-world `map`-style semantics: inserting keys on first encounter, incrementing counts on subsequent encounters, and producing output in a deterministic sorted order.

## What You Will Implement

Write a program that reads lines of text from standard input, tokenises each line into words (splitting on spaces), counts how many times each word appears, and prints each word along with its count — **sorted alphabetically by word**.

Words should be treated as **case-insensitive**: `"Hello"` and `"hello"` are the same word. Strip any leading/trailing punctuation characters (`.`, `,`, `!`, `?`, `'`, `"`, `;`, `:`) from each token before counting.

## Skills Practiced

- Using `map<string, int>` (or `unordered_map` + sorting) for frequency aggregation.
- The `operator[]` default-insert pattern: `freq[word]++`.
- Normalising keys (lowercase, strip punctuation) before lookup.
- Iterating a `map` in sorted key order.

## Example

Given input:
```
hello world
Hello again world
```

Expected output:
```
again 1
hello 2
world 2
```

## Instructions

1. Read all input until EOF.
2. For each line, split on space characters to get tokens.
3. Normalise each token: lowercase all letters, strip leading and trailing punctuation.
4. Skip any token that becomes empty after stripping.
5. Increment the count for that word.
6. After all input is read, print each `word count` pair in ascending alphabetical order, one per line, separated by a single space.

Open the prompt file for full constraints, edge cases, and test data.
