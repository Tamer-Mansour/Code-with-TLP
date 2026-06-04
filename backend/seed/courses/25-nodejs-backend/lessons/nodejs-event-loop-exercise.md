# Event Loop Execution Order Simulator

The Node.js event loop determines the exact order in which your code runs. Mastering this order is essential for debugging async bugs and writing correct concurrent code.

## How the Event Loop Orders Work

When Node.js executes code, tasks are placed in different queues and executed in a strict priority order:

1. **Synchronous code** — runs immediately on the call stack
2. **`process.nextTick` callbacks** — drain completely before any other async work
3. **Promise microtasks** — `.then` / `async-await` continuations
4. **Macrotasks** — `setTimeout`, `setImmediate`, I/O callbacks

```js
console.log("1 sync");

Promise.resolve().then(() => console.log("3 microtask"));

process.nextTick(() => console.log("2 nextTick"));

setTimeout(() => console.log("4 macrotask"), 0);

console.log("1b sync");
```

Output:
```
1 sync
1b sync
2 nextTick
3 microtask
4 macrotask
```

## Why This Matters

Consider this common bug:

```js
let result;
db.query("SELECT 1", (err, rows) => {
  result = rows;
});
console.log(result); // undefined — callback hasn't run yet!
```

The database callback is an I/O macrotask. By the time `console.log` runs (synchronously), the callback has not fired. Understanding execution order prevents this class of bug.

## Common Misconception

`process.nextTick` fires before Promise microtasks, even though both are "microtasks" conceptually. The name is misleading — it does not mean "next iteration of the event loop." It means "before the next phase of this iteration."

```js
Promise.resolve().then(() => console.log("promise"));
process.nextTick(() => console.log("nextTick"));
// Output: nextTick, then promise
```

## The Phases in Detail

```
   ┌─────────────────────────────┐
   │           timers            │  ← setTimeout, setInterval
   ├─────────────────────────────┤
   │     pending callbacks       │  ← some system I/O errors
   ├─────────────────────────────┤
   │       idle, prepare         │  ← internal use
   ├─────────────────────────────┤
   │           poll              │  ← retrieve new I/O events
   ├─────────────────────────────┤
   │           check             │  ← setImmediate
   ├─────────────────────────────┤
   │      close callbacks        │  ← socket.on('close')
   └─────────────────────────────┘
        ↑                    |
        └── nextTick + Promise microtasks drain between each phase
```

## Further Reading

- **"Become a Node.js Developer" by Thomas Gentilhomme** — https://fraxken.github.io/ebook_nodejs/ — covers the event loop deeply, libuv internals, and execution order edge cases that most beginner resources skip.
- **"Eloquent JavaScript" Chapter 20** — https://eloquentjavascript.net/ — introduces Node fundamentals including async I/O patterns with practical examples.

## Exercise

In this exercise you will simulate the event loop execution order given a sequence of task registrations. Your job is to predict the exact output order: SYNC first, then NEXTTICK, then MICROTASK, then MACROTASK.
