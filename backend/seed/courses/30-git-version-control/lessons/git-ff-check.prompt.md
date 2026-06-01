# Fast-Forward Merge Decider

Given a commit graph and two commits, determine whether merging the second into the first would be a fast-forward.

A merge is a **fast-forward** when `base` is an ancestor of (or equal to) `target` in the commit graph.

## Input

```
N
<commit 1>
<commit 2 with parents>
...
<commit N with parents>
<base> <target>
```

- `N` is the number of commits (1 ≤ N ≤ 1000).
- Each commit line is `<name> <parent1> <parent2> ...` (zero or more parents).
- Final line is two commit names: base and target.

## Output

- `FAST-FORWARD` — if `base` is an ancestor of `target` (or equal).
- `MERGE` — otherwise (a true merge commit would be needed).

## Examples

Input:

```
3
A
B A
C B
A C
```

Output: `FAST-FORWARD` (A is ancestor of C through B)

Input:

```
4
A
B A
C A
D C
B D
```

Output: `MERGE` (B branches off A, D is on another line — no ancestor relationship)

Input:

```
1
A
A A
```

Output: `FAST-FORWARD` (same commit)

Input:

```
5
A
B A
C B
D C
E D
A E
```

Output: `FAST-FORWARD`

## Notes

- Commit names are single uppercase letters or short strings.
- The graph is a DAG (no cycles); commits list their parents.
- "A is ancestor of B" includes the case A == B.
