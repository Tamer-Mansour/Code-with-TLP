# memo, useMemo, useCallback

React re-renders components when state or parent props change. Most of the time this is fine. When a render is expensive — or causes a cascade — you reach for memoization.

## React.memo — skip re-rendering

```tsx
const ExpensiveList = React.memo(function ExpensiveList({ items }: { items: Item[] }) {
  return <ul>{items.map(...)}</ul>;
});
```

`React.memo` shallow-compares the new props with the previous. If they're equal (by `===`), it skips the render.

A common pitfall: the parent passes a new function or object every render, breaking memoization:

```tsx
<ExpensiveList items={items} onClick={() => console.log("hi")} />
//                                ^ new function every render — memo busted
```

## useCallback — stable function identity

```tsx
const onClick = useCallback(() => {
  doSomething(id);
}, [id]);

<ExpensiveList items={items} onClick={onClick} />
```

Returns the same function as long as deps haven't changed. Useful when you pass a function to a memoized child.

## useMemo — cache expensive computation

```tsx
const sortedItems = useMemo(
  () => items.slice().sort((a, b) => a.score - b.score),
  [items]
);
```

The sort runs only when `items` changes. For cheap computations, skip — `useMemo` has its own overhead.

A handful of cases where `useMemo` clearly pays off:

- Sorting/filtering a long list.
- Building data structures used by children that depend on referential equality.
- Heavy calculations (parsing, layout, math).

## The default: don't memoize

`useMemo`, `useCallback`, and `React.memo` add complexity. The vast majority of components render quickly enough that memoization is unnecessary. Profile first; memoize when it matters.

The exceptions:

1. You **know** the child is expensive and props rarely change.
2. You're passing data into a context value (memoize the context value).
3. The component is in a hot render path (deeply nested, often re-rendered).

## React Compiler (experimental)

The forthcoming React Compiler auto-inserts memoization. When it's stable you may write `useMemo` and `useCallback` much less. Until then: profile + apply intentionally.

## React Profiler

Open DevTools → Profiler tab → record an interaction. The flame graph shows what re-rendered and why. Click a component → "Why did this render?" tells you the prop that changed.

This is the right way to find performance issues. Guessing without profiling almost always memoizes the wrong things.

## Lists — virtualization

If you render a list of 10,000+ items, the bottleneck isn't React's diff — it's rendering 10,000 DOM nodes. Use **virtualization**: render only what's on screen.

- **react-window** — lightweight.
- **TanStack Virtual** — modern, framework-agnostic.

```tsx
import { useVirtualizer } from "@tanstack/react-virtual";

const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 40,
});
```

Now only ~30 items are mounted at any time, regardless of list length.

## Concurrent rendering (React 18+)

React 18 added **concurrent features** that help long renders feel responsive:

- `useTransition` — mark some state updates as non-urgent.
- `useDeferredValue` — display a stale value while the next is computed.
- Suspense + streaming on the server side.

Most apps don't need them. When you do, they're powerful.
