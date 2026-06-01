# Label Selector Matcher

Implement Kubernetes-style label matching.

## Input

```
<selector>             comma-separated key=value pairs (AND semantics)
N                       number of pods (1 ≤ N ≤ 100)
<pod 1>                 "<name> <labels>" or just "<name>" if no labels
<pod 2>
... N lines
```

Each pod line: pod name, a space, comma-separated `key=value` labels (or empty after the space).

## Output

Pod names that match the selector, in input order, one per line.

If nothing matches, print `NONE`.

## Examples

Input:

```
app=web
3
pod-1 app=web,env=prod
pod-2 app=api
pod-3 app=web,env=dev
```

Output:

```
pod-1
pod-3
```

Input:

```
app=web,env=prod
3
pod-1 app=web,env=prod
pod-2 app=web,env=dev
pod-3 app=web,env=prod,version=v2
```

Output:

```
pod-1
pod-3
```

Input:

```
app=nope
2
pod-1 app=web
pod-2 app=api
```

Output:

```
NONE
```

## Notes

- A pod matches if **every** selector key/value is present in the pod's labels.
- Extra labels on the pod are fine.
- A pod with no labels matches only an empty selector (which won't appear in tests).
