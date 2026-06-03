# Functions, Scope, and Closures

Functions are the building blocks of every JavaScript program. Understanding how they are declared, where their variables live, and how closures let inner functions "remember" outer values will unlock a large portion of the JavaScript patterns you will encounter in real projects and in Spring Boot frontend work.

## Declaring Functions

JavaScript gives you three main ways to create a function, each with subtle differences.

```javascript
// 1. Function declaration — hoisted to the top of its scope
function add(a, b) {
  return a + b;
}

// 2. Function expression — not hoisted; assigned to a variable
const multiply = function (a, b) {
  return a * b;
};

// 3. Arrow function (ES6+) — concise syntax; does NOT bind its own `this`
const divide = (a, b) => a / b;

console.log(add(3, 4));        // 7
console.log(multiply(3, 4));   // 12
console.log(divide(12, 4));    // 3
```

**Arrow function body rules:**
- Single expression with no braces: the expression is returned implicitly.
- Multi-statement body: wrap in `{ }` and use an explicit `return`.

## Scope

Scope determines which variables are visible at a given point in code. JavaScript has three levels:

| Scope level | Created by | Keyword(s) | Accessible from |
|---|---|---|---|
| Global | Outside any function or block | `var`, `let`, `const` | Everywhere in the file |
| Function | Inside a `function` body | `var`, `let`, `const` | Only within that function |
| Block | Inside `{ }` (if, for, etc.) | `let`, `const` | Only within that block |

`var` ignores block scope — it leaks out to the enclosing function. Prefer `let` and `const` to avoid surprises.

```javascript
function processOrder(quantity) {
  const TAX_RATE = 0.15;          // function-scoped constant

  if (quantity > 10) {
    let discount = 0.1;           // block-scoped — invisible outside the if
    console.log(discount);        // 0.1  ✓
  }

  // console.log(discount);       // ReferenceError — discount is out of scope

  return quantity * (1 + TAX_RATE);
}

console.log(processOrder(5));     // 5.75
console.log(processOrder(15));    // 17.25
```

### Hoisting

Function **declarations** are hoisted completely — you can call them before the line where they appear. Function **expressions** and **arrow functions** assigned to `const` or `let` are NOT hoisted.

```javascript
console.log(greet("Alice"));   // "Hello, Alice"  — works because greet is hoisted

function greet(name) {
  return `Hello, ${name}`;
}

// console.log(farewell("Alice")); // ReferenceError — farewell is not yet initialised
const farewell = (name) => `Goodbye, ${name}`;
```

## Closures

A **closure** is formed when an inner function references a variable from its outer (enclosing) function's scope. The inner function keeps a live reference to that variable even after the outer function has returned.

```javascript
function makeCounter(start = 0) {
  let count = start;              // outer variable

  return {
    increment() { count += 1; },
    decrement() { count -= 1; },
    value()     { return count; }
  };
}

const counter = makeCounter(10);
counter.increment();
counter.increment();
counter.decrement();
console.log(counter.value());    // 11

const otherCounter = makeCounter();
console.log(otherCounter.value()); // 0  — independent closure, separate `count`
```

Each call to `makeCounter` creates its own `count` variable. The returned object closes over that specific variable, so `counter` and `otherCounter` never interfere with each other.

### Realistic Use Case — Private State in a Module

```javascript
function createCart() {
  const items = [];                        // private — not exposed directly

  return {
    addItem(name, price) {
      items.push({ name, price });
    },
    total() {
      return items.reduce((sum, item) => sum + item.price, 0);
    },
    summary() {
      return items.map(i => `${i.name}: $${i.price.toFixed(2)}`).join("\n");
    }
  };
}

const cart = createCart();
cart.addItem("Keyboard", 49.99);
cart.addItem("Mouse", 29.99);
console.log(cart.total());    // 79.98
console.log(cart.summary());
// Keyboard: $49.99
// Mouse: $29.99
```

Callers cannot access `items` directly — it is effectively private, enforced purely by scope.

## Default Parameters and Rest/Spread

```javascript
// Default parameter
function greetUser(name, role = "Student") {
  return `Welcome, ${name} (${role})!`;
}
console.log(greetUser("Sara"));            // Welcome, Sara (Student)!
console.log(greetUser("Ali", "Mentor"));   // Welcome, Ali (Mentor)!

// Rest parameter — collects remaining arguments into an array
function sumAll(...numbers) {
  return numbers.reduce((acc, n) => acc + n, 0);
}
console.log(sumAll(1, 2, 3, 4, 5));  // 15
```

## Common Mistakes

- **Using `var` in loops** — `var` is function-scoped, so all iterations share the same variable. Use `let` instead.
- **Assuming arrow functions bind `this`** — they inherit `this` from the surrounding context, which is intentional for callbacks but can be surprising if you expect them to behave like regular methods.
- **Accidentally creating global variables** — omitting `let`/`const`/`var` inside a function silently creates a global: `count = 0` is a bug; `let count = 0` is correct.
- **Over-capturing in closures** — closing over a large object keeps it in memory as long as the closure lives. Hold only the data you need.

## Summary

Function declarations are hoisted; `let`/`const` function expressions are not. Block-scoped `let` and `const` prevent the variable-leaking pitfalls of `var`. Closures let inner functions retain access to outer variables across calls, enabling patterns like private state, counters, and factory functions — patterns you will encounter throughout modern JavaScript and in the browser-side code of Spring Boot applications.
