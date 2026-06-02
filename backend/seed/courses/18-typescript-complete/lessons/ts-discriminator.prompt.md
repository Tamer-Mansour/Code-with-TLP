# Union Type Discriminator

You are given `N` JSON objects. Each has a `"kind"` field. Process each object by its kind:

- `"circle"` with `radius`: output `circle area=<π*r² rounded to 2 decimal places>`
- `"rectangle"` with `width` and `height`: output `rectangle area=<w*h rounded to 2 decimal places>`
- `"text"` with `value` (string): output `text len=<length of value>`
- Any other kind: output `unknown`

## Input format

```
N
<JSON line 1>
...
<JSON line N>
```

## Output format

One result per line, in order.

## Example

Input:
```
2
{"kind":"circle","radius":3}
{"kind":"text","value":"hi"}
```

Output:
```
circle area=28.27
text len=2
```
