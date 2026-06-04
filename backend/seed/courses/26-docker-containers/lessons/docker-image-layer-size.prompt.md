# Image Layer Size Calculator

## Problem

Docker images are built as a stack of read-only layers. Each layer records file operations. Because of **copy-on-write semantics**, modifying or deleting a file in a higher layer does **not** reclaim the space from lower layers — the original bytes stay on disk.

Given a sequence of layers and their file operations, compute:

1. **Total image size on disk** — sum of bytes written across all layers. Each ADD or MODIFY writes bytes to that layer. DELETE writes 0 bytes (whiteout marker has negligible size).
2. **Effective filesystem size** — bytes visible when a container runs: only the topmost version of each file counts, and deleted files are excluded entirely.

## Input Format

```
N
<layer_number>
<OPERATION> <filename> <bytes>
...

<layer_number>
<OPERATION> <filename> <bytes>
...

```

- First line: `N` — number of layers.
- Each layer begins with its layer number (1, 2, 3, ...) on its own line.
- Followed by one or more operation lines: `ADD`, `MODIFY`, or `DELETE`, then filename, then byte count.
- Layers are separated by a blank line.

Operations:
- `ADD filename bytes` — new file added in this layer (bytes > 0).
- `MODIFY filename bytes` — file overwritten in this layer with new content (bytes > 0).
- `DELETE filename 0` — file removed (whiteout marker, 0 bytes written to this layer).

## Output Format

```
Total image size: X bytes
Effective filesystem size: Y bytes
```

## Example

Input:
```
3
1
ADD /app/base.py 1000
ADD /app/utils.py 500

2
MODIFY /app/base.py 1200
ADD /app/new.py 800

3
DELETE /app/utils.py 0
MODIFY /app/new.py 900
```

Output:
```
Total image size: 4400 bytes
Effective filesystem size: 2100 bytes
```

**Explanation:**

Layer 1 writes: 1000 + 500 = 1500 bytes  
Layer 2 writes: 1200 + 800 = 2000 bytes  
Layer 3 writes: 0 + 900 = 900 bytes  
Total on disk: 1500 + 2000 + 900 = **4400 bytes**

Effective filesystem (topmost state):
- `/app/base.py` → last modified in layer 2 at 1200 bytes ✓
- `/app/utils.py` → deleted in layer 3 → excluded
- `/app/new.py` → last modified in layer 3 at 900 bytes ✓
Total effective: 1200 + 900 = **2100 bytes**

## Constraints

- 1 ≤ N ≤ 10
- 1 ≤ total operations ≤ 50
- Byte values are non-negative integers.
- Each filename is a Unix-style absolute path.
- A file will not be ADDed twice without a DELETE in between.
