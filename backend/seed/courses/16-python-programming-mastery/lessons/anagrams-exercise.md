# Group Anagrams

A classic Python problem that exercises dicts, sorting, and string handling.

Given a list of words, group those that are anagrams of each other.

The trick: an anagram's *sorted character tuple* is a canonical key.

```python
"eat" -> "aet"
"tea" -> "aet"
"tan" -> "ant"
"ate" -> "aet"
```

Words with the same key go in the same group.

See the prompt for the exact I/O contract.
