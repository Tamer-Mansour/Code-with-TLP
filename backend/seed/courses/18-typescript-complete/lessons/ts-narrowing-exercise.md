# Exercise: Union Type Discriminator

In this exercise you simulate what TypeScript does when narrowing a discriminated union at compile time — but at runtime using Python.

You will receive a list of JSON objects, each having a `kind` field plus variant-specific fields. Your task is to process each object according to its `kind` and produce a single output string per object.

## Supported kinds

| `kind` | Required extra field | Output format |
|---|---|---|
| `"circle"` | `radius` (number) | `circle area=<X>` where X = π × r² rounded to 2 decimal places |
| `"rectangle"` | `width`, `height` (numbers) | `rectangle area=<X>` where X = width × height rounded to 2 decimal places |
| `"text"` | `value` (string) | `text len=<N>` where N = length of `value` |
| unknown kind | — | `unknown` |

## Input format

```
N
<json object 1>
<json object 2>
...
<json object N>
```

## Output format

One line per object in the same order.

## Example

**Input:**
```
3
{"kind":"circle","radius":5}
{"kind":"rectangle","width":4,"height":3}
{"kind":"text","value":"hello"}
```

**Output:**
```
circle area=78.54
rectangle area=12.00
text len=5
```
