# Functions and Arrow Functions

## Function declarations

```javascript
function add(a, b) {
  return a + b;
}
```

Hoisted — you can call `add` before its declaration in the file.

## Function expressions

```javascript
const add = function(a, b) {
  return a + b;
};
```

Not hoisted (the `const` declaration is in the temporal dead zone until evaluated).

## Arrow functions

```javascript
const add = (a, b) => a + b;
const square = x => x * x;          // single param, parens optional
const noop = () => {};
const greet = name => `hi, ${name}`;
const obj = name => ({ name });     // wrap object literal in parens
```

Multi-line arrow:

```javascript
const f = (x, y) => {
  const sum = x + y;
  return sum * 2;
};
```

Without the explicit `return` the function returns `undefined`.

## Differences from `function`

Arrow functions:

- **Don't bind their own `this`.** They inherit `this` from the enclosing scope. Huge in event handlers and class methods.
- **Don't have `arguments`.** Use rest params (`...args`) instead.
- **Can't be constructors.** No `new MyArrow()`.
- **Don't have a `prototype` property.**

Use arrows for callbacks, transformations, and short utilities. Use `function` (or class methods) when you want `this` rebound (event listeners on DOM elements, prototype methods).

## Default arguments

```javascript
function greet(name = "world") {
  return `hello, ${name}`;
}
```

## Rest parameters

```javascript
function log(level, ...messages) {
  console.log(level, messages.join(" "));
}
log("INFO", "user", "logged", "in");
// INFO user logged in
```

## Spread at call sites

```javascript
const nums = [1, 2, 3];
Math.max(...nums);             // 3
const merged = [...a, ...b];
const clone = { ...obj };
```

## Destructuring parameters

```javascript
function fetchUser({ id, includeOrders = false }) {
  ...
}

fetchUser({ id: 42, includeOrders: true });
```

Improves call sites (named arguments) and avoids parameter order bugs.

## Returning multiple values

JavaScript doesn't have tuples. Return an object:

```javascript
function divmod(a, b) {
  return { quotient: Math.floor(a / b), remainder: a % b };
}
const { quotient, remainder } = divmod(10, 3);
```

Or an array if it's truly positional:

```javascript
function range() { return [start, end]; }
const [start, end] = range();
```

## Immediately Invoked Function Expressions (IIFE)

The old way to create a private scope:

```javascript
(function() {
  // ...
})();
```

Mostly obsolete since modules and `let`/`const`. You may still see it in legacy code.
