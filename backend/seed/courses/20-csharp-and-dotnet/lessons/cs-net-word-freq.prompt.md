# Word Frequency Counter

Given a single line of space-separated lowercase words (only `a-z` characters), count the frequency of each word. Print each word and its count, sorted by frequency **descending**, then alphabetically **ascending** for ties.

## Input

One line of space-separated lowercase words.

## Output

One line per unique word: `<word> <count>`, in the order described above.

## Example

**Input:**
```
the cat sat on the mat the cat
```

**Output:**
```
the 3
cat 2
mat 1
on 1
sat 1
```

## Constraints

- 1 ≤ number of words ≤ 10,000
- Words consist of lowercase `a-z` letters only
- At least one word in the input
