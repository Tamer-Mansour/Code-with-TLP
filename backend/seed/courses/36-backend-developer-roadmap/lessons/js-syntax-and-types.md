# JavaScript Syntax and Types

JavaScript is a dynamically typed, interpreted language that runs natively in every browser and on the server via Node.js. Unlike Java, you do not declare types — the engine infers them at runtime. That flexibility is powerful, but it demands a solid understanding of how values and types behave to avoid subtle bugs.

## Program Structure

JavaScript has no mandatory class or entry-point boilerplate. A `.js` file is a sequence of statements executed top-to-bottom.

```javascript
// hello.js
const greeting = "Hello, World!";
console.log(greeting);  // Hello, World!
```

Run it with Node.js:

```bash
node hello.js
```

Key syntax rules:
- Statements optionally end with a semicolon `;`. Use them — relying on Automatic Semicolon Insertion (ASI) can produce surprising results.
- Blocks are enclosed in curly braces `{}`.
- JavaScript is **case-sensitive**: `myVar` and `myvar` are different identifiers.
- Single-line comments use `//`; multi-line comments use `/* … */`.

## Variable Declarations: `var`, `let`, and `const`

Modern JavaScript (ES6+) provides three declaration keywords. Prefer `const` and `let`; avoid `var`.

| Keyword | Scope       | Reassignable | Hoisted          | When to use                          |
|---------|-------------|--------------|------------------|--------------------------------------|
| `var`   | Function    | Yes          | Yes (to `undefined`) | Legacy code only — avoid             |
| `let`   | Block `{}`  | Yes          | No (TDZ*)        | Values that will change              |
| `const` | Block `{}`  | No           | No (TDZ*)        | Default for most declarations        |

*TDZ = Temporal Dead Zone — accessing the variable before its declaration throws a `ReferenceError`.

```javascript
const MAX_RETRIES = 3;       // cannot be reassigned
let attempts = 0;            // will be incremented in a loop

attempts += 1;
// MAX_RETRIES = 5;          // TypeError: Assignment to constant variable
```

## The Seven Primitive Types

JavaScript has seven primitives. They are immutable values — not objects.

| Type        | Example literal          | `typeof` result  |
|-------------|--------------------------|------------------|
| `number`    | `42`, `3.14`, `NaN`      | `"number"`       |
| `bigint`    | `9007199254740993n`      | `"bigint"`       |
| `string`    | `"hello"`, `'hi'`, `` `template` `` | `"string"` |
| `boolean`   | `true`, `false`          | `"boolean"`      |
| `undefined` | `undefined`              | `"undefined"`    |
| `null`      | `null`                   | `"object"` (bug*)|
| `symbol`    | `Symbol("id")`           | `"symbol"`       |

*`typeof null === "object"` is a long-standing language quirk kept for backwards compatibility. Test for null explicitly: `value === null`.

```javascript
console.log(typeof 42);          // "number"
console.log(typeof "hello");     // "string"
console.log(typeof true);        // "boolean"
console.log(typeof undefined);   // "undefined"
console.log(typeof null);        // "object"  ← historical bug
console.log(typeof {});          // "object"
console.log(typeof []);          // "object"  ← arrays are objects
```

## Numbers and Arithmetic

JavaScript has a single `number` type (IEEE 754 double-precision float) for both integers and decimals.

```javascript
const a = 10;
const b = 3;

console.log(a + b);   // 13
console.log(a - b);   // 7
console.log(a * b);   // 30
console.log(a / b);   // 3.3333333333333335  (no integer division!)
console.log(a % b);   // 1  (remainder)
console.log(a ** b);  // 1000  (exponentiation, ES7)

// Special numeric values
console.log(1 / 0);        // Infinity
console.log(-1 / 0);       // -Infinity
console.log(0 / 0);        // NaN
console.log(isNaN(0 / 0)); // true
```

Unlike Java, there is no separate integer type. For integers beyond `Number.MAX_SAFE_INTEGER` (2^53 - 1), use `bigint` by appending `n`:

```javascript
const big = 9_007_199_254_740_993n;  // accurate beyond safe integer range
```

## Strings and Template Literals

Strings can use single quotes, double quotes, or backtick template literals. Backticks (ES6) allow embedded expressions and multi-line strings without escape sequences.

```javascript
const name = "Alice";
const lang = 'JavaScript';

// Concatenation (old style)
console.log("Hello, " + name + "! Welcome to " + lang + ".");

// Template literal (preferred)
console.log(`Hello, ${name}! Welcome to ${lang}.`);

// Expression inside ${}
const a = 5, b = 10;
console.log(`${a} + ${b} = ${a + b}`);  // 5 + 10 = 15

// Useful string methods
const s = "  backend dev  ";
console.log(s.trim());           // "backend dev"
console.log(s.trim().toUpperCase());  // "BACKEND DEV"
console.log("hello".includes("ell")); // true
console.log("hello".replace("l", "r")); // "herlo" (first match only)
console.log("a,b,c".split(","));  // ["a", "b", "c"]
```

## Type Coercion

JavaScript automatically converts types in some operations — this is called **implicit coercion** and is a leading source of bugs.

```javascript
// + with a string triggers string concatenation
console.log("5" + 3);    // "53"  — number coerced to string
console.log("5" - 3);    // 2     — string coerced to number (- has no string meaning)

// == performs coercion; === does not
console.log(0 == false);   // true   — coercion
console.log(0 === false);  // false  — strict, no coercion

// Falsy values: false, 0, "", null, undefined, NaN
// Everything else is truthy
console.log(Boolean(""));        // false
console.log(Boolean("0"));       // true  ← non-empty string is truthy
console.log(Boolean(null));      // false
console.log(Boolean([]));        // true  ← empty array is truthy
```

**Always use `===` (strict equality) and `!==` (strict inequality)** to avoid coercion surprises.

## Explicit Type Conversion

When you need to change a type deliberately, use explicit conversion functions.

```javascript
// To number
Number("42");      // 42
Number("3.14");    // 3.14
Number("");        // 0
Number("abc");     // NaN
parseInt("10px");  // 10  (stops at first non-numeric character)
parseFloat("3.7em"); // 3.7

// To string
String(42);        // "42"
String(true);      // "true"
(42).toString();   // "42"

// To boolean
Boolean(0);        // false
Boolean("hello");  // true
```

## Common Mistakes and Best Practices

- **Use `const` by default.** Only switch to `let` when you need to reassign. This makes intent clear and prevents accidental mutation.
- **Never use `==`.** Always compare with `===` to avoid implicit coercion bugs.
- **Check for `NaN` with `Number.isNaN()`.** `NaN === NaN` is `false`, so `===` cannot detect it.
- **`typeof null` is `"object"`.** To check for null, always use `value === null`.
- **Template literals over concatenation.** Backtick strings are more readable and less error-prone when embedding variables.
- **Semicolons are optional but use them.** ASI is not always intuitive; explicit semicolons remove ambiguity.

## Summary

JavaScript's type system is dynamic and permissive — `const`/`let` scope, seven primitives, a single `number` type for all math, and template literals for readable strings are the foundation every backend developer must own before writing any logic.
