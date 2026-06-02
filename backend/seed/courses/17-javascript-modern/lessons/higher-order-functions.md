# Higher-Order Functions

A **higher-order function** is any function that either takes a function as an argument, returns a function, or both. Because JavaScript treats functions as first-class values, higher-order functions are everywhere in everyday code.

## Functions as Arguments

The classic example is the built-in array methods you already use:

```javascript
const numbers = [1, 2, 3, 4, 5];

// forEach, map, filter, reduce all accept a callback
numbers.forEach(n => console.log(n));
const doubled = numbers.map(n => n * 2);      // [2, 4, 6, 8, 10]
const evens   = numbers.filter(n => n % 2 === 0);  // [2, 4]
const total   = numbers.reduce((acc, n) => acc + n, 0); // 15
```

The function passed in (the callback) defines *what to do*; the higher-order function defines *when and how often* to do it.

## Functions as Return Values

Returning a function lets you build **configured, specialized** functions on demand:

```javascript
function multiplier(factor) {
  return (n) => n * factor;
}

const triple = multiplier(3);
const half   = multiplier(0.5);

triple(10);  // 30
half(10);    // 5
```

`multiplier` is higher-order because it *returns* a function. The returned function closes over `factor` — that is a closure working together with a higher-order function.

## Composing Behavior

Higher-order functions shine when you compose small pieces:

```javascript
const compose = (...fns) => (x) => fns.reduceRight((v, f) => f(v), x);

const add1    = x => x + 1;
const double  = x => x * 2;
const square  = x => x * x;

const transform = compose(add1, double, square);
transform(3);
// square(3) = 9 → double(9) = 18 → add1(18) = 19
```

`compose` is a higher-order function that takes functions and returns a new combined function.

## Practical Example: Middleware / Decorators

The pattern is used everywhere in Node.js (Express middleware), React (HOCs, hooks), and logging:

```javascript
function withLogging(fn) {
  return function (...args) {
    console.log(`Calling ${fn.name} with`, args);
    const result = fn(...args);
    console.log(`${fn.name} returned`, result);
    return result;
  };
}

function add(a, b) { return a + b; }

const loggedAdd = withLogging(add);
loggedAdd(3, 4);
// Calling add with [3, 4]
// add returned 7
```

`withLogging` wraps any function transparently — a classic **decorator** pattern.

## `once` — Run a Function Only One Time

```javascript
function once(fn) {
  let called = false;
  let result;
  return (...args) => {
    if (!called) {
      called = true;
      result = fn(...args);
    }
    return result;
  };
}

const initialize = once(() => {
  console.log("init!");
  return 42;
});

initialize();  // "init!"  → 42
initialize();  // → 42  (no log)
```

## `partial` — Pre-fill Arguments

```javascript
function partial(fn, ...preset) {
  return (...rest) => fn(...preset, ...rest);
}

function greet(greeting, name) {
  return `${greeting}, ${name}!`;
}

const sayHello = partial(greet, "Hello");
sayHello("Tamer");  // "Hello, Tamer!"
sayHello("Sara");   // "Hello, Sara!"
```

## Summary

| Pattern | Description |
|---------|-------------|
| Callback | Pass a function to be called later |
| Factory | Return a new specialized function |
| Decorator | Wrap a function to add behavior |
| Compose/Pipe | Combine functions into a pipeline |
| Partial application | Pre-fill some arguments |

Higher-order functions are the foundation of functional programming in JavaScript. Once you recognize the pattern, you will find it in React hooks, Express routes, RxJS operators, and virtually every large JavaScript codebase.
