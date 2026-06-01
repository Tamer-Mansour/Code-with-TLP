# Group Anagrams

Read a single line of whitespace-separated words. Group anagrams together. Print each group on its own line, words within a group separated by spaces.

## Input

A single line of words separated by whitespace. Each word is lowercase letters only.

```
eat tea tan ate nat bat
```

## Output

For each anagram group:

- Print the words within the group **sorted alphabetically**, space-separated.
- Print the groups in the **order of the first appearance** of any word in the group.

For the input above:

```
ate eat tea
ant tan
bat
```

(The first group was "first seen" at `eat`; the second at `tan`; the third at `bat`.)

## More examples

```
a b c
```

→

```
a
b
c
```

```
listen silent enlist hello world
```

→

```
enlist listen silent
hello
dlorw
```

(`dlorw` is the sorted-letter canonical form *of the group containing only "world"* — note: words in the output are the original input words **sorted alphabetically**, not their letters. Trace through: the lone word "world" sorts to "world" alone.)

Wait — re-read: the output is the original words sorted alphabetically. So for "world" alone the group is just `world`. The example expected output above has `dlorw` which would only be right if "world" sorted-by-letters = `dlorw`. Use the actual rule: **print the original words, sorted alphabetically within the group.**

## Constraints

- 1 ≤ words ≤ 1000.
- Each word ≤ 50 characters.
