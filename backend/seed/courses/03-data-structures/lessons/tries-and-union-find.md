# Tries & Union-Find

## Tries (Prefix Trees)

A **trie** (pronounced "try", from re**trie**val) is a tree where each edge represents one character of a string. Every root-to-marked-node path spells a complete word. Tries excel at prefix-based operations that hash tables cannot support efficiently.

```
Words inserted: "cat", "car", "card", "care", "bat"

root
├── c
│   └── a
│       ├── t [END]          ← "cat"
│       └── r [END]          ← "car"
│           ├── d [END]      ← "card"
│           └── e [END]      ← "care"
└── b
    └── a
        └── t [END]          ← "bat"
```

Shared prefixes share physical nodes: "car", "card", and "care" all share the `c → a → r` path, saving both space and lookup time.

### Trie Node

```python
class TrieNode:
    def __init__(self):
        self.children = {}     # char → TrieNode
        self.is_end = False    # True if this node terminates a word
        self.count = 0         # optional: how many words pass through this node
```

Using a `dict` for children supports any alphabet. For lowercase English only, an array `[None]*26` (indexed by `ord(ch) - ord('a')`) is faster in practice.

### Insert — O(L)

Walk character by character, creating nodes as needed. Set `is_end = True` at the final character's node.

```python
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
```

### Search (Exact Match) — O(L)

```python
    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end   # True only if this node ends a word
```

### Starts-With (Prefix Query) — O(L)

```python
    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True   # any match, whether full word or prefix
```

### Count Words with Prefix — O(L + matches)

```python
    def count_prefix(self, prefix: str) -> int:
        """Count words in the trie that start with prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return 0
            node = node.children[ch]
        # DFS from this node to count all ends
        return self._count_ends(node)

    def _count_ends(self, node) -> int:
        total = 1 if node.is_end else 0
        for child in node.children.values():
            total += self._count_ends(child)
        return total
```

### Trie Complexity

| Operation          | Time  | Space      | Notes                           |
|--------------------|-------|------------|---------------------------------|
| Insert word        | O(L)  | O(L)       | at most L new nodes             |
| Search word        | O(L)  | O(1)       | no allocation needed            |
| Prefix query       | O(L)  | O(1)       |                                 |
| Delete word        | O(L)  | O(1)       | mark is_end=False; prune leaves |
| All words sharing prefix| O(L+M)| O(M) | M = total chars in results      |
| Space (n words)    | —     | O(total chars) | shared prefixes save space |

L = length of the queried word/prefix.

### Trie vs. Hash Map

| Feature                | Hash Map (`dict`)  | Trie               |
|------------------------|--------------------|--------------------|
| Exact word lookup      | O(L) avg           | O(L)               |
| Prefix existence query | O(L * n) worst     | O(L)               |
| Autocomplete           | O(n * L)           | O(L + results)     |
| Lexicographic ordering | O(n log n)         | O(n) DFS           |
| Space                  | O(n * L)           | O(total chars)     |

**Use a trie** when you need prefix queries, autocomplete, spell-checking, or IP routing tables. **Use a hash map** when you only need exact-word lookup.

### Common Trie Bug

Confusing "word not in trie" with "prefix not in trie". Always check `node.is_end` for exact match, not just successful traversal.

---

## Union-Find (Disjoint Set Union — DSU)

**Union-Find** maintains a dynamic partition of n elements into disjoint sets. It answers connectivity queries efficiently: "Are elements x and y in the same component?"

### The Problem it Solves

Given a sequence of `merge(x, y)` and `connected(x, y)` queries on n elements, Union-Find answers each in nearly O(1). A naive approach (BFS/DFS per query) costs O(V + E) per `connected` call — far too slow for repeated queries.

### Core Operations

- `find(x)` — return the **representative** (root) of the set containing x.
- `union(x, y)` — merge the sets containing x and y. Returns False if already merged.
- `connected(x, y)` — equivalent to `find(x) == find(y)`.

### Naïve Implementation — O(n) per operation

```python
class UnionFindNaive:
    def __init__(self, n: int):
        self.parent = list(range(n))   # parent[i] = i means i is its own root

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        self.parent[ry] = rx
        return True
```

Without optimisations, `find` can take O(n) on a degenerate tree (chain). We need two key improvements.

### Optimisation 1: Path Compression

During `find`, flatten the path from x to its root — make every node on the path point directly to the root:

```python
def find(self, x: int) -> int:
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])   # recurse then flatten
    return self.parent[x]
```

After path compression, subsequent `find` calls on any node along that path are O(1).

### Optimisation 2: Union by Rank (Size)

Always attach the **shorter tree under the taller tree** (or smaller under larger when using size). This keeps trees shallow:

```python
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n    # upper bound on height

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False   # same component already
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx          # ensure rx has higher rank
        self.parent[ry] = rx        # attach smaller tree under larger
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1      # only increment when ranks are equal
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

### Why It Works — Step-by-Step Example

```
Initial: parent = [0, 1, 2, 3, 4]   rank = [0, 0, 0, 0, 0]

union(0, 1):  roots 0 and 1, equal rank → parent[1]=0, rank[0]=1
              parent = [0, 0, 2, 3, 4]   rank = [1, 0, 0, 0, 0]

union(2, 3):  roots 2 and 3, equal rank → parent[3]=2, rank[2]=1
              parent = [0, 0, 2, 2, 4]   rank = [1, 0, 1, 0, 0]

union(0, 2):  find(0)=0, find(2)=2. rank[0]=rank[2]=1 → parent[2]=0, rank[0]=2
              parent = [0, 0, 0, 2, 4]   rank = [2, 0, 1, 0, 0]

find(3):  parent[3]=2, parent[2]=0 → path compress: parent[3]=0
          parent = [0, 0, 0, 0, 4]
```

### Complexity with Both Optimisations

| Operation      | Time          | Space |
|----------------|---------------|-------|
| find(x)        | O(α(n)) ≈ O(1)| O(1)  |
| union(x, y)    | O(α(n)) ≈ O(1)| O(1)  |
| connected(x,y) | O(α(n)) ≈ O(1)| O(1)  |
| Total for m ops| O(m · α(n))   | O(n)  |

α(n) is the **inverse Ackermann function** — the slowest-growing function in mathematics. For all practical values of n (even n = 10^80), α(n) ≤ 4. Combined path compression + union by rank gives the theoretically optimal Union-Find.

### Union-Find Applications

**1. Count connected components:**

```python
def count_components(n: int, edges: list) -> int:
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return len({uf.find(i) for i in range(n)})
```

**2. Cycle detection in undirected graph:**

```python
def has_cycle(n: int, edges: list) -> bool:
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):   # already connected → adding this edge creates a cycle
            return True
    return False
```

**3. Kruskal's Minimum Spanning Tree (overview):**
Sort edges by weight, then greedily add the cheapest edge that connects two previously disconnected components (checked with Union-Find). Stop when n−1 edges have been added.

### Union-Find vs. BFS/DFS for Connectivity

| Scenario                          | Union-Find         | BFS/DFS             |
|-----------------------------------|--------------------|---------------------|
| Static graph, many queries        | O(α) per query     | O(V+E) per query    |
| Dynamic graph (edges added online)| O(α) per edge/query| Must rebuild        |
| Single connectivity query         | O(α)               | O(V+E), same order  |
| Find shortest path                | Cannot             | BFS can             |
| Detect directed cycle             | Cannot             | DFS can             |
