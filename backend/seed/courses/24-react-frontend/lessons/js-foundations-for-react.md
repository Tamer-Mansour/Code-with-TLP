# JavaScript Foundations for React

React is a JavaScript library, not a replacement for JavaScript. Before hooks, JSX, and components click, you need fluency in the modern JavaScript (ES6+) features that React uses everywhere. This lesson covers the essential JS you will see in every React codebase.

## Arrow Functions and Concise Syntax

```js
// Traditional
function double(x) { return x * 2; }

// Arrow — same thing, less syntax
const double = x => x * 2;

// Implicit return for expressions
const greet = name => `Hello, ${name}!`;

// Multi-statement body requires explicit return
const clamp = (val, min, max) => {
  if (val < min) return min;
  if (val > max) return max;
  return val;
};
```

Arrow functions **do not have their own `this`** — they inherit `this` from the enclosing scope. This matters in class components but is rarely an issue with functional components.

## Destructuring

Extract values from objects and arrays cleanly:

```js
// Object destructuring
const { name, age } = user;
const { name: userName, role = "guest" } = user; // rename + default

// Array destructuring
const [first, second, ...rest] = items;
const [count, setCount] = useState(0); // ← React uses this constantly

// Function parameter destructuring (React props)
function Button({ label, onClick, disabled = false }) {
  return <button onClick={onClick} disabled={disabled}>{label}</button>;
}
```

## Spread and Rest Operators

```js
// Spread: copy and extend
const updated = { ...user, age: 31 };           // new object with age overridden
const combined = [...listA, ...listB];           // merge arrays
const withNew = [...items, newItem];             // append

// Rest: collect remaining arguments
function log(first, ...others) {
  console.log(first, others); // others is an array
}

// In JSX: forward all extra props
function Input({ label, ...inputProps }) {
  return <label>{label}<input {...inputProps} /></label>;
}
```

Spread is how React state is updated immutably — you produce a new object rather than mutating the old one.

## Modules (ESM import / export)

```js
// Named exports
export function add(a, b) { return a + b; }
export const PI = 3.14159;

// Default export
export default function App() { ... }

// Importing
import App from './App';                      // default
import { add, PI } from './math';             // named
import * as math from './math';               // namespace
import React, { useState, useEffect } from 'react';  // mixed
```

React's entire ecosystem is ESM. Understanding imports is essential for building component trees.

## Array Methods: map, filter, reduce

These are the backbone of React rendering logic:

```js
const numbers = [1, 2, 3, 4, 5];

const doubled  = numbers.map(n => n * 2);        // [2, 4, 6, 8, 10]
const evens    = numbers.filter(n => n % 2 === 0); // [2, 4]
const sum      = numbers.reduce((acc, n) => acc + n, 0); // 15

// In JSX:
<ul>
  {users
    .filter(u => u.active)
    .map(u => <li key={u.id}>{u.name}</li>)}
</ul>
```

## Promises and async / await

React applications fetch data from APIs asynchronously. Promises and `async/await` are the standard way to handle this:

```js
// Promise chain
fetch('/api/users')
  .then(res => res.json())
  .then(data => setUsers(data))
  .catch(err => setError(err.message));

// async/await — cleaner for complex flows
async function loadUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    throw err; // re-throw so callers can handle it
  }
}
```

## Closures and Lexical Scope

A **closure** is a function that "closes over" variables from its surrounding scope. In React, every component is a closure over its state and props:

```js
function makeCounter(start) {
  let count = start;
  return {
    increment: () => ++count,
    value: () => count,
  };
}
```

This is why `useState` setters called inside `setTimeout` can see stale values — the callback closed over the `count` at render time. Using the functional updater form `setCount(c => c + 1)` avoids the problem because it receives the latest value rather than the closure value.

## Recommended References

- [Eloquent JavaScript, 4th Edition](https://eloquentjavascript.net/) by Marijn Haverbeke — chapters on functions, closures, higher-order functions, and async are directly relevant.
- [The Modern JavaScript Tutorial](https://javascript.info/) — a comprehensive, free, sandbox-based reference for every ES6+ feature.
