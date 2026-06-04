# useState Batching — How React Groups State Updates

One of the subtler aspects of `useState` is that state updates are **asynchronous and batched**. Understanding this prevents a class of hard-to-debug bugs.

## What Is Batching?

When you call a state setter multiple times inside a single React event handler, React does not re-render after each call. Instead it collects all updates, applies them together, and triggers exactly **one** re-render at the end:

```tsx
function handleClick() {
  setA(1); // no render yet
  setB(2); // no render yet
  setC(3); // one render here
}
```

This is efficient — three separate renders would be wasteful.

## The Stale Closure Trap

Because state is not updated immediately, reading the variable right after calling the setter gives the **old** value:

```tsx
const [count, setCount] = useState(0);

function handleClick() {
  setCount(count + 1); // count is still 0 here
  setCount(count + 1); // count is STILL 0, not 1
  // result: count becomes 1, not 2
}
```

Both calls see `count = 0` because the variable is captured in the closure at render time. The fix is the **functional updater form**:

```tsx
function handleClick() {
  setCount(c => c + 1); // receives latest queued value
  setCount(c => c + 1); // receives 1, returns 2
  // result: count becomes 2
}
```

## React 18 Automatic Batching

Before React 18, batching only happened inside React-managed event handlers. Calls inside `setTimeout`, Promises, or native events each triggered their own render:

```tsx
// Before React 18 — triggers two renders
setTimeout(() => {
  setA(1); // render
  setB(2); // render
}, 0);
```

React 18 introduces **automatic batching** everywhere. The same code now produces one render. If you specifically need synchronous flushing, use `flushSync` from `react-dom`:

```tsx
import { flushSync } from "react-dom";

flushSync(() => setA(1)); // render immediately
flushSync(() => setB(2)); // render immediately
```

`flushSync` is rare — it exists for interop with non-React code (third-party animations, etc.).

## Non-functional vs Functional Updates

| Pattern | Reads from | Safe for concurrent updates? |
|---------|-----------|------------------------------|
| `setState(state + 1)` | Closure value at render time | No — stale in batches |
| `setState(s => s + 1)` | Latest queued value | Yes |

Always prefer the functional form whenever the new state depends on the previous value.

## Practice Exercise

The exercise below simulates how React processes batched updates. Within each batch, all operations read the state value from the **start** of the batch — exactly mirroring the naive `setState(state + 1)` anti-pattern. Work through the examples manually before coding to cement your mental model.

> **Further reading:** [react.dev — Queueing a Series of State Updates](https://react.dev/learn/queueing-a-series-of-state-updates) explains the batching queue with detailed step-by-step diagrams.
