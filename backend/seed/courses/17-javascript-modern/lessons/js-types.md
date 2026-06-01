# Types and Coercion

JavaScript has **seven primitive types** plus the **object** type. Everything you assign to a variable is one of these.

## Primitives

- `string` — `"hello"` or `'hello'` or template literal `` `hello ${x}` ``
- `number` — `42`, `3.14`, `NaN`, `Infinity` (all 64-bit floats — no separate int)
- `bigint` — `42n` (for integers beyond 2^53)
- `boolean` — `true`, `false`
- `undefined` — uninitialized
- `null` — explicit "nothing"
- `symbol` — unique opaque values, mostly for advanced metaprogramming

## Objects

Everything else: arrays, functions, dates, regex, plain `{}`. Functions are first-class objects you can pass around.

```javascript
const user   = { name: "Alice", age: 30 };
const nums   = [1, 2, 3];
const add    = (a, b) => a + b;
const today  = new Date();
const rx     = /^foo/i;
```

## typeof

```javascript
typeof "x"          // "string"
typeof 42           // "number"
typeof true         // "boolean"
typeof undefined    // "undefined"
typeof Symbol()     // "symbol"
typeof null         // "object"   ← historic bug
typeof []           // "object"
typeof function(){} // "function"
```

Two well-known quirks: `typeof null === "object"`, and arrays are objects.

## Numbers

```javascript
1 + 1               // 2
0.1 + 0.2           // 0.30000000000000004   (IEEE-754)
1 / 0               // Infinity
0 / 0               // NaN
Number("42")        // 42
parseInt("42px")    // 42
Number.isInteger(3) // true
Number.isNaN(NaN)   // true
```

For money use **integers in the smallest unit** (cents), not floats.

## Strings

Immutable. Template literals interpolate:

```javascript
const name = "Alice";
`hello, ${name}`;       // "hello, Alice"
`${1+1}`;               // "2"
```

Multi-line strings via backticks just work.

## null vs undefined

- `undefined` — "the language hasn't set this yet."
- `null` — "the programmer says nothing is here."

Conventionally, return `null` to signal "explicit absence" and use `undefined` for missing parameters or fields. Many real-world codebases mix them; modern TypeScript pushes you toward `undefined` everywhere.

## Coercion

JavaScript coerces between types aggressively. Some operators trigger it:

```javascript
"5" + 1      // "51"   (string concat wins for +)
"5" - 1      // 4      (arithmetic forces numbers)
"5" == 5     // true   (loose equality coerces)
"5" === 5    // false  (strict equality does not)
+"3"         // 3      (unary + forces number)
!!"hello"    // true   (double-not -> boolean)
```

The rule of thumb: **use `===`**, **explicitly cast**, **avoid `+` on mixed types**. Modern JS (and TypeScript) makes this easy to do consistently.
