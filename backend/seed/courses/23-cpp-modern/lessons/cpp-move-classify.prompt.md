# Move Semantics Value Category Classifier

Given a list of C++ expressions with category hints, classify each as `LVALUE`, `RVALUE`, or `XVALUE` based on Modern C++ value category rules.

## Rules

| Hint | Classification |
|------|---------------|
| `VAR` | Named variable → **LVALUE** |
| `LIT` | Literal value → **RVALUE** |
| `CALL_VAL` | Function returning `T` → **RVALUE** |
| `CALL_REF` | Function returning `T&` → **LVALUE** |
| `MOVE` | `std::move(x)` result → **XVALUE** |
| `NAMED_RREF` | Named rvalue reference variable → **LVALUE** |
| `TEMP` | Temporary object inline → **RVALUE** |

## Input Format

- Line 1: integer `N`
- Lines 2..N+1: `expression|hint` (expression and hint separated by `|`)

## Output Format

One line per expression:
```
expression: CATEGORY
```

## Example

**Input:**
```
7
x|VAR
42|LIT
getValue()|CALL_VAL
getRef()|CALL_REF
std::move(x)|MOVE
rref_var|NAMED_RREF
MyClass()|TEMP
```

**Output:**
```
x: LVALUE
42: RVALUE
getValue(): RVALUE
getRef(): LVALUE
std::move(x): XVALUE
rref_var: LVALUE
MyClass(): RVALUE
```

## Constraints

- `1 <= N <= 100`
- Each hint is one of: `VAR`, `LIT`, `CALL_VAL`, `CALL_REF`, `MOVE`, `NAMED_RREF`, `TEMP`
- Expression strings contain no `|` characters
