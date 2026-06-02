# Destructuring and Spread / Rest

Destructuring and the spread/rest operators (`...`) are among the most used ES2015+ features. They make reading values from arrays and objects far more concise.

## Array Destructuring

```javascript
const rgb = [255, 128, 0];

// Old way
const r = rgb[0], g = rgb[1], b = rgb[2];

// Destructuring
const [red, green, blue] = rgb;
console.log(red, green, blue);  // 255 128 0
```

Skip elements with an empty slot:

```javascript
const [, second, , fourth] = [1, 2, 3, 4];
// second = 2, fourth = 4
```

Swap two variables without a temp:

```javascript
let a = 1, b = 2;
[a, b] = [b, a];
// a = 2, b = 1
```

## Object Destructuring

```javascript
const user = { name: "Sara", age: 28, role: "admin" };

const { name, role } = user;
console.log(name, role);  // "Sara" "admin"
```

Rename while destructuring:

```javascript
const { name: username, age: years } = user;
console.log(username, years);  // "Sara" 28
```

Default values when a key is missing:

```javascript
const { theme = "light", fontSize = 14 } = {};
// theme = "light", fontSize = 14
```

Nested destructuring:

```javascript
const { address: { city, zip } } = { address: { city: "Cairo", zip: "11511" } };
console.log(city);  // "Cairo"
```

## Rest in Destructuring

Collect the remaining elements or properties:

```javascript
const [first, ...rest] = [1, 2, 3, 4, 5];
console.log(first);  // 1
console.log(rest);   // [2, 3, 4, 5]

const { name: n, ...details } = user;
console.log(details);  // { age: 28, role: "admin" }
```

## Spread Operator

Spread expands an iterable (array, string) or object into individual elements.

**Copying and merging arrays:**

```javascript
const a = [1, 2, 3];
const b = [...a, 4, 5];     // [1, 2, 3, 4, 5]
const copy = [...a];         // shallow copy
```

**Spreading into function arguments:**

```javascript
function sum(x, y, z) { return x + y + z; }
const nums = [1, 2, 3];
sum(...nums);  // 6
```

**Copying and merging objects:**

```javascript
const defaults = { color: "blue", size: "M" };
const overrides = { size: "L", weight: "bold" };

const merged = { ...defaults, ...overrides };
// { color: "blue", size: "L", weight: "bold" }
```

Later keys overwrite earlier ones — order matters.

## Function Parameter Destructuring

A common pattern in React/Node code is to destructure function parameters directly:

```javascript
function greet({ name, greeting = "Hello" }) {
  return `${greeting}, ${name}!`;
}

greet({ name: "Tamer" });           // "Hello, Tamer!"
greet({ name: "Ali", greeting: "Hi" }); // "Hi, Ali!"
```

## Quick Reference

| Syntax | Meaning |
|--------|---------|
| `const [a, b] = arr` | Array destructuring |
| `const { x, y } = obj` | Object destructuring |
| `const { x: newName } = obj` | Rename during destructure |
| `const { x = 5 } = obj` | Default value |
| `const [head, ...tail] = arr` | Rest in array |
| `const { a, ...rest } = obj` | Rest in object |
| `[...arr1, ...arr2]` | Spread / merge arrays |
| `{ ...obj1, ...obj2 }` | Spread / merge objects |

Destructuring is especially valuable in function signatures, loop variables (`for (const { id, name } of users)`), and when working with APIs that return deeply nested objects.
