# Type Coercion Oracle

Test your knowledge of JavaScript's `typeof` operator and the difference between loose (`==`) and strict (`===`) equality.

This exercise covers quirks that trip up experienced developers, and are regularly tested in JavaScript interviews.

## Key Concepts

### typeof quirks

```javascript
typeof null          // "object"   ← famous historic bug
typeof NaN           // "number"   ← NaN is paradoxically typeof number
typeof undefined     // "undefined"
typeof []            // "object"   ← arrays are objects
typeof function(){}  // "function" ← functions are callable objects
```

### NaN is never equal to itself

```javascript
NaN === NaN  // false
NaN == NaN   // false
// Use Number.isNaN() instead:
Number.isNaN(NaN)  // true
```

### Loose equality (==) surprises

The `==` operator applies complex Abstract Equality Comparison rules:

```javascript
null == undefined   // true  (special rule: only these two)
null == 0           // false (null only loosely equals null/undefined)
0 == false          // true  (both coerce to 0)
'' == false         // true  (both coerce to 0)
0 == ''             // true  ('' converts to 0)
```

## Task

Given N JavaScript expressions, output what each evaluates to as JavaScript would.

Supported forms:
- `typeof X` — returns the type string
- `A == B` — returns `true` or `false`
- `A === B` — returns `true` or `false`

## Example

**Input:**
```
6
typeof null
typeof NaN
NaN == NaN
null == undefined
null === undefined
0 == false
```

**Output:**
```
object
number
false
true
false
true
```

## Constraints

- 1 ≤ N ≤ 50
- Values are from: `null`, `undefined`, `NaN`, `42`, `hello`, `true`, `false`, `[]`, `{}`
- Equality operands are from: `null`, `undefined`, `0`, `false`, `''`, `NaN`

## Further Reading

- [You Don't Know JS Yet](https://github.com/getify/You-Dont-Know-JS) — Chapters on Types and Coercion give the full specification-level explanation of how `==` works.
- [Speaking JavaScript](https://exploringjs.com/es5/toc.html) — Exceptional depth on coercion rules.
