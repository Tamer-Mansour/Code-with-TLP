# The Event Loop

JavaScript is **single-threaded**. There is one call stack. So how does the browser handle clicks while running an animation while fetching data? The **event loop**.

## The model

```
       ┌──────────────┐
       │  call stack  │  <-- where JS runs synchronously
       └──────┬───────┘
              │ (when empty)
              ▼
       ┌──────────────┐
       │ microtask Q  │  <-- promise callbacks
       └──────┬───────┘
              │ (drained completely)
              ▼
       ┌──────────────┐
       │  macrotask Q │  <-- setTimeout, I/O, UI events
       └──────────────┘
```

Each "tick":

1. Run synchronous code until the stack is empty.
2. Drain **all** microtasks (promise callbacks, queueMicrotask).
3. Pick **one** macrotask, run it.
4. Render (in browsers).
5. Repeat.

## A worked example

```javascript
console.log("A");

setTimeout(() => console.log("B"), 0);

Promise.resolve().then(() => console.log("C"));

console.log("D");
```

Output:

```
A
D
C
B
```

- `A` and `D` are sync.
- `C` is a microtask — drained before any macrotask.
- `B` is a macrotask (setTimeout 0).

## Why this matters

**Long synchronous work blocks everything.**

```javascript
function spin(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}
button.onclick = () => spin(2000);
```

Clicking the button freezes the page for 2 seconds — no rendering, no other clicks, no animations.

Break long work into chunks (`setTimeout` between batches, `requestIdleCallback`, or move to a Web Worker).

## Microtasks can starve macrotasks

A promise that resolves to another promise queues another microtask. A loop of `.then` chains will run forever without ever letting a `setTimeout` fire. Pathological, but it happens.

## Node's event loop (Libuv)

Node's loop is similar but with multiple **phases** per tick:

```
timers -> pending I/O -> poll (waiting for I/O) -> check (setImmediate) -> close
```

After each phase, microtasks (`process.nextTick`, promise callbacks) drain. `process.nextTick` has higher priority than promise microtasks — a subtle Node-specific detail.

## What you should actually do

- Don't run long sync work on the main thread.
- Don't expect "exact" timing from `setTimeout` — it's a *minimum* delay.
- Trust the event loop; don't try to outsmart it with `setTimeout(fn, 0)` tricks unless you understand why.
- Use `queueMicrotask` for "later but before the next macrotask" — rarely needed but precise.

## requestAnimationFrame

Specifically for animations:

```javascript
function tick() {
  draw();
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
```

The browser calls your callback right before the next paint, syncing your render with the display.

## Web Workers — actual parallelism

For real CPU-bound work, spawn a Worker:

```javascript
const w = new Worker("worker.js");
w.postMessage({ data });
w.onmessage = (e) => console.log(e.data);
```

Workers run on a separate thread. They can't touch the DOM; they communicate by messages. Use for heavy computation that must not freeze the UI.
