# Exercise: Trie Prefix Search

Build a trie from a dictionary, then answer queries classifying each string as a word, prefix, or neither.

## Approach

Insert all dictionary words into the trie. For each query:

1. Walk the trie character by character.
2. If any character is missing from the trie: `NONE`.
3. If all characters are found and `is_end` is True at the final node: `WORD`.
4. Otherwise (path exists but not a complete word): `PREFIX`.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

def classify(root, query):
    node = root
    for ch in query:
        if ch not in node.children:
            return "NONE"
        node = node.children[ch]
    return "WORD" if node.is_end else "PREFIX"
```
