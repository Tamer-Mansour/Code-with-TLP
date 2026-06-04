# Props Propagation Depth Analyzer

Prop drilling occurs when a prop must pass through intermediate components that do not use it. Analyze a component tree to measure how deep a given prop must travel.

## Input

- Lines of the form `Parent Child` (one relationship per line).
- A **blank line** separator.
- A final line with two component names: `SOURCE CONSUMER` — where the prop originates and where it is consumed.

## Output

If a path exists from SOURCE to CONSUMER in the tree:

```
Path length: <N>
Intermediate (drilling) components: <M>
```

Where:
- `N` = number of components on the path from SOURCE to CONSUMER (inclusive of both endpoints).
- `M` = number of intermediate components that receive the prop but do not use it = `N - 2` (minimum 0; equals 0 when SOURCE is the direct parent of CONSUMER).

If no path exists from SOURCE to CONSUMER, print:

```
NO PATH
```

## Examples

**Example 1**

Input:
```
App Page
Page Section
Section Panel
Panel Widget
Widget Button

App Button
```

Output:
```
Path length: 6
Intermediate (drilling) components: 4
```

(Path: App → Page → Section → Panel → Widget → Button, 6 nodes)

**Example 2 — Direct parent-child**

Input:
```
App Child

App Child
```

Output:
```
Path length: 2
Intermediate (drilling) components: 0
```

**Example 3 — No path**

Input:
```
App Child
Other Sibling

App Sibling
```

Output:
```
NO PATH
```

**Example 4 — Three-level drill**

Input:
```
Root A
A B
B C

Root C
```

Output:
```
Path length: 4
Intermediate (drilling) components: 2
```

## Notes

- The tree is directed (parent to child only). BFS from SOURCE downward.
- SOURCE and CONSUMER are guaranteed to be component names that appear in the relationship list.
- There are no cycles.
