# == vs === and Truthiness

JavaScript has two equality operators. One is sane. One is famous for unpredictable corner cases.

## Strict equality: `===`

Compares value and type. No coercion. Always use this.

```javascript
1 === 1               // true
1 === "1"             // false
null === undefined    // false
NaN === NaN           // false   (NaN is never equal to anything, including itself)
```

For NaN, use `Number.isNaN(x)`.

For `undefined`/`null` checks together, use `x == null` — the *only* legitimate use of `==`, because it's true for both:

```javascript
if (value == null) { ... }       // true if null OR undefined
```

## Loose equality: `==`

Coerces operands before comparing. Behaviors include:

```javascript
0 == false            // true
"" == false           // true
" " == false          // true   (whitespace string -> 0 -> false)
"0" == false          // true
[] == false           // true
[0] == false          // true
"5" == 5              // true
1 == "1"              // true
null == undefined     // true   (only loose case worth knowing)
[] == ![]             // true (!)
```

You can derive every rule from the spec, but it's not worth it. **Use `===`.**

## Truthiness

`Boolean(x)` is `false` for:

```
false, 0, -0, 0n, "", null, undefined, NaN
```

Everything else is `true`. Notably:

```javascript
Boolean([])   // true
Boolean({})   // true
Boolean("0")  // true   ← non-empty string
```

A common pattern:

```javascript
if (user) {           // exists, not null/undefined
  process(user);
}
```

## Logical operators return operands, not booleans

```javascript
"hello" || "world"    // "hello"
""       || "world"   // "world"
"hello" && "world"    // "world"
""       && "world"   // ""
```

Useful for defaults:

```javascript
const name = props.name || "Anonymous";
```

But `||` falls back on *all* falsy values — including `0` and `""`. If `0` is a valid value:

```javascript
const port = config.port ?? 3000;   // nullish coalescing — only null/undefined
```

`??` (3+ years old at this point) is what you usually want for "default if missing."

## Optional chaining

```javascript
user?.profile?.email          // undefined if any link is null/undefined
user?.fetch?.()               // call fetch() only if user has it
arr?.[0]                      // arr[0] only if arr is not null/undefined
```

Pairs perfectly with `??`:

```javascript
const email = user?.profile?.email ?? "n/a";
```

## Object equality

JavaScript compares objects by **reference**, not by value:

```javascript
{a: 1} === {a: 1}     // false
const x = {a: 1};
x === x               // true
```

For value equality of arbitrary objects, you reach for a library (`lodash.isEqual`, `fast-deep-equal`) or `JSON.stringify` for simple cases.
