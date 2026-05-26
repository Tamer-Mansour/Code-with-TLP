# Hash Tables

A **hash table** (hash map, dictionary) maps arbitrary keys to values with O(1) average-case lookup, insertion, and deletion. It is the most widely-used data structure in practical software — Python's `dict`, JavaScript objects, Java's `HashMap`, and most caches are built on this idea.

## The Core Idea

1. Allocate an array of `capacity` **buckets**.
2. To store key `k`, compute `index = hash(k) % capacity`.
3. Store the `(key, value)` pair at `buckets[index]`.
4. To look up key `k`, recompute the same index and check `buckets[index]`.

```
Keys:     "cat"  "dog"  "fox"
hash%8:     3      6      1

Buckets:  [ _,  "fox",  _,  "cat",  _,  _,  "dog",  _ ]
Index:      0     1     2     3     4   5     6      7
```

A good hash function makes this O(1) on average. The worst case — all keys collide in one bucket — degrades to O(n).

## Hash Functions

A good hash function must be:
- **Deterministic:** `hash(k)` always returns the same value for the same `k`.
- **Uniform:** distributes keys evenly across all buckets, minimising collisions.
- **Fast:** computed in O(1) or O(L) for a key of length L.

Common strategies:
- **Integer keys:** `h = key % capacity` (simple, works well if capacity is prime).
- **String keys:** polynomial rolling hash — `h = sum(ord(c) * p^i for i, c in enumerate(key)) % capacity`. Python's built-in uses a variant of SipHash.
- **Composite keys (tuples):** hash each component and combine with XOR or FNV.

```python
# Python's built-in hash is randomised per process for security
print(hash("hello"))   # different every run (unless PYTHONHASHSEED=0)

# For reproducible hashing in competitive programming:
# PYTHONHASHSEED=0 python script.py
```

### What is Hashable?

An object is hashable if it has a `__hash__` method that returns the same integer for its lifetime and an `__eq__` that is consistent. In Python:
- Hashable (can be dict keys or set elements): `int`, `float`, `str`, `tuple` (of hashables), `frozenset`.
- **Not hashable**: `list`, `dict`, `set` — mutable objects whose content (and thus logical identity) can change.

## Collision Handling

Two different keys producing the same bucket index is a **collision**. There are two classical resolution strategies.

### Strategy 1: Separate Chaining

Each bucket holds a linked list (or dynamic array) of all `(key, value)` pairs that hash there.

```
bucket[3]: → ("cat", 5) → ("hat", 7) → None
```

Lookup walks the chain comparing keys. If the load factor α is low, chains are short and lookup is O(1). Worst case: all n keys in one chain — O(n).

```python
class ChainingHashMap:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.n = 0

    def _index(self, key):
        return hash(key) % self.capacity

    def put(self, key, val) -> None:
        bucket = self.buckets[self._index(key)]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, val)   # update
                return
        bucket.append((key, val))        # insert
        self.n += 1

    def get(self, key, default=None):
        for k, v in self.buckets[self._index(key)]:
            if k == key:
                return v
        return default
```

### Strategy 2: Open Addressing — Linear Probing

All entries live inside the main array. On collision, probe the next slot (index+1, +2, …) until an empty slot is found. Index wraps modulo capacity.

```
Insert "cat" hashes to index 3 — occupied by "hat".
Probe index 4 — empty → store "cat" here.
```

Deletion is tricky: you cannot just clear the slot (that would break probe chains). Instead, use a **tombstone** sentinel value. Future lookups skip tombstones; future inserts can reuse them.

```python
EMPTY = object()
TOMBSTONE = object()

class LinearProbingMap:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.keys = [EMPTY] * capacity
        self.vals = [None] * capacity
        self.n = 0

    def _probe(self, key):
        idx = hash(key) % self.capacity
        while self.keys[idx] is not EMPTY and self.keys[idx] != key:
            if self.keys[idx] is TOMBSTONE:
                pass  # keep probing
            idx = (idx + 1) % self.capacity
        return idx

    def put(self, key, val) -> None:
        idx = self._probe(key)
        if self.keys[idx] is EMPTY:
            self.n += 1
        self.keys[idx] = key
        self.vals[idx] = val

    def delete(self, key) -> None:
        idx = self._probe(key)
        if self.keys[idx] is not EMPTY:
            self.keys[idx] = TOMBSTONE
            self.n -= 1
```

**Quadratic probing** (`+1, +4, +9, ...`) and **double hashing** (`idx + k*step`) reduce **primary clustering** — the tendency of linear probing to form long consecutive runs.

## Load Factor and Resizing

The **load factor** α = n / capacity governs the expected number of probes per operation.

| Load factor α | Expected probes (linear probing) | Typical state     |
|---------------|----------------------------------|-------------------|
| 0.25          | ~1.2                             | Mostly empty      |
| 0.50          | ~1.5                             | Good balance      |
| 0.75          | ~2.5                             | Python dict limit |
| 0.90          | ~5.5                             | Too crowded       |
| 1.00          | ∞                                | Unusable          |

When α exceeds a threshold (0.75 for Python `dict`, 0.75 for Java `HashMap`), the table **rehashes**: allocate a new array of ~2× capacity, recompute the index for every existing entry, and reinsert. Rehashing is O(n) but amortised O(1) per insert.

Python's `dict` uses a compact open-addressing scheme with pseudo-random probing (not linear), which keeps cache locality while avoiding primary clustering.

## Complexity Summary

| Operation | Average | Worst (all same hash) | Space |
|-----------|---------|----------------------|-------|
| Insert    | O(1)    | O(n)                 | O(n)  |
| Lookup    | O(1)    | O(n)                 | —     |
| Delete    | O(1)    | O(n)                 | —     |

The worst case is rare in practice with a good hash function and load factor control.

## Python dict and set

Python's `dict` is a heavily-optimised open-addressing hash table (compact dict since Python 3.6 preserves insertion order as a side effect):

```python
# dict: key → value
freq = {}
for word in ["apple", "banana", "apple", "cherry"]:
    freq[word] = freq.get(word, 0) + 1
# {"apple": 2, "banana": 1, "cherry": 1}

# From Python 3.7+, dicts are ordered by insertion order
for k, v in freq.items():
    print(k, v)   # apple 2, banana 1, cherry 1

# set: keys only, no values — backed by a hash table
seen = set()
for x in [1, 2, 2, 3, 1]:
    seen.add(x)
# {1, 2, 3}
```

`dict` and `set` both support O(1) average `in` tests:

```python
if "apple" in freq:     # O(1)
    print(freq["apple"])

# collections.defaultdict avoids KeyError on missing keys
from collections import defaultdict
groups = defaultdict(list)
groups["fruits"].append("apple")   # no KeyError even if key didn't exist
```

## Common Hash Table Patterns

### Frequency Count

```python
from collections import Counter

words = "the cat sat on the mat the cat".split()
c = Counter(words)
print(c.most_common(2))   # [('the', 3), ('cat', 2)]
```

### Two-Sum — O(n)

Find two indices whose values sum to `target`:

```python
def two_sum(nums: list, target: int) -> tuple:
    seen = {}   # value → index
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return (seen[complement], i)
        seen[x] = i
    return None

print(two_sum([2, 7, 11, 15], 9))   # (0, 1)
```

### Anagram Grouping — O(n · L)

```python
from collections import defaultdict

def group_anagrams(words: list) -> list:
    groups = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))   # canonical form
        groups[key].append(w)
    return list(groups.values())

print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))
# [['eat','tea','ate'], ['tan','nat'], ['bat']]
```

### Sliding Window Uniqueness — O(n)

Find the length of the longest substring with no repeated characters:

```python
def longest_unique(s: str) -> int:
    last_seen = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

print(longest_unique("abcabcbb"))  # 3 ("abc")
```

## Hash Table vs. Other Structures

| Comparison            | Hash Table | Sorted Array | BST (balanced) |
|-----------------------|-----------|--------------|----------------|
| Lookup                | O(1) avg  | O(log n)     | O(log n)       |
| Insert                | O(1) avg  | O(n)         | O(log n)       |
| Delete                | O(1) avg  | O(n)         | O(log n)       |
| Ordered iteration     | No*       | Yes          | Yes (in-order) |
| Range queries         | No        | O(log n + k) | O(log n + k)   |
| Prefix queries        | No        | No           | No (use trie)  |

*Python `dict` preserves insertion order but does not support key-range queries.

Use a hash table when you need fast point lookups and don't need ordering. Use a sorted structure (BST, sorted list) when you need range queries or in-order iteration.
