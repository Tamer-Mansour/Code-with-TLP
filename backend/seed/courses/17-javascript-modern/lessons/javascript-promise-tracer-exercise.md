# Promise Chain Tracer

Understand JavaScript's event loop execution order by tracing the output of synchronous code, Promise microtasks, and setTimeout macrotasks.

## The Execution Model

JavaScript processes tasks in a strict order each "tick":

```
1. Run all synchronous code (call stack)
2. Drain ALL microtasks (Promise .then callbacks, queueMicrotask)
3. Run ONE macrotask (setTimeout, setInterval, I/O)
4. Render (browser only)
5. Repeat
```

### Example

```javascript
console.log('start');            // SYNC

setTimeout(() => {
  console.log('timeout');        // MACRO
}, 0);

Promise.resolve().then(() => {
  console.log('promise');        // MICRO
});

console.log('end');              // SYNC
```

Output:
```
start
end
promise
timeout
```

Notice: `promise` (microtask) prints **before** `timeout` (macrotask) even though `setTimeout(fn, 0)` was registered first.

## Task

Given N task registrations, determine the order in which their labels would be printed.

**Task types:**
- `SYNC label` — synchronous code, runs immediately in registration order
- `MICRO label` — a Promise microtask, runs after all sync code, before macrotasks
- `MACRO label` — a setTimeout macrotask, runs last

All tasks of the same type execute in the order they were registered.

## Example

**Input:**
```
5
SYNC start
MACRO timeout1
MICRO promise1
SYNC end
MICRO promise2
```

**Output:**
```
start
end
promise1
promise2
timeout1
```

## Constraints

- 1 ≤ N ≤ 100
- Labels are alphanumeric strings

## Further Reading

- [The Modern JavaScript Tutorial — Event Loop](https://javascript.info/event-loop) — Excellent visual walkthrough of microtask vs macrotask queues.
- [Eloquent JavaScript Chapter 11](https://eloquentjavascript.net/11_async.html) — Asynchronous Programming, covers the callback-to-async/await arc with worked examples.
