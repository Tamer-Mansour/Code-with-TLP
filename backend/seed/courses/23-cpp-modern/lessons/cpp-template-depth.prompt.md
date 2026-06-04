# Template Instantiation Depth Checker

Simulate recursive template instantiation and detect depth limit violations.

## Input Format

- Line 1: two integers `M` (template definitions) and `LIMIT` (max allowed depth)
- Lines 2..M+1: `TemplateName N sub1 sub2 ... subN`
  - `N` is the number of sub-templates this template instantiates
  - A sub-template name of `BASE` means no further instantiation (leaf node)
- Last line: the name of the starting template

## Output Format

Three lines:
1. `Unique instantiations: K`
2. `DEPTH_OK` or `DEPTH_EXCEEDED`
3. The instantiation path where limit was first exceeded (` -> ` separated), or `N/A`

## Example

**Input:**
```
4 3
Factorial 1 Factorial
MyPair 2 Vector Map
Vector 1 BASE
Map 1 BASE
MyPair
```

**Output:**
```
Unique instantiations: 3
DEPTH_OK
N/A
```

## Notes

- Count only **unique** template names actually reached during DFS from the start node
- Depth starts at 1 for the starting template
- If a template has already been visited (cycle or shared dependency), do not re-visit it — just stop that branch
- If the depth limit is exceeded, record the path at the first node where `depth > LIMIT`
- `BASE` nodes are not counted as instantiations

## Constraints

- `1 <= M <= 50`
- `1 <= LIMIT <= 20`
- Template names are alphanumeric (no spaces)
- The starting template always appears in the definitions
