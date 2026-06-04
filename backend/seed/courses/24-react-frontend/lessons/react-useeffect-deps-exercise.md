# useEffect and Dependency Arrays

The `useEffect` hook's dependency array is the most important — and most misunderstood — part of effects. Getting it right is the difference between a component that works correctly and one that has subtle stale-data or infinite-loop bugs.

## How the Dependency Array Works

```tsx
useEffect(() => {
  // side effect body
  return () => { /* cleanup */ };
}, [dep1, dep2]);
```

React compares each dependency value between renders using `Object.is` (reference equality for objects). If **any** dependency changed, the effect body runs again. If none changed, the effect is skipped.

| Dependency array | When effect runs |
|-----------------|-----------------|
| Omitted | After every render |
| `[]` | Once, after the initial render (mount) |
| `[a, b]` | After mount, and whenever `a` or `b` changes |

## The Rules

**Include every reactive value used in the effect.** A reactive value is any variable from the component scope: state, props, context values, or anything derived from them.

```tsx
// Wrong — userId is used but not listed
useEffect(() => {
  fetch(`/api/users/${userId}`).then(...)
}, []); // stale userId on prop change

// Correct
useEffect(() => {
  fetch(`/api/users/${userId}`).then(...)
}, [userId]); // re-fetches whenever userId changes
```

React's ESLint plugin (`eslint-plugin-react-hooks`) enforces this automatically. Trust it.

## Cleanup and the Double-Mount in Strict Mode

Every effect that sets up a subscription, starts a timer, or initiates a fetch should return a cleanup function:

```tsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err.message);
    });
  return () => controller.abort(); // cleanup: cancel in-flight request
}, [url]);
```

In React 18 Strict Mode (development only), React intentionally mounts every component **twice** — running the effect, then the cleanup, then the effect again. This surfaces missing cleanups early, before they become production bugs.

## Object and Function Dependencies

Avoid putting unstable objects or functions in the dependency array:

```tsx
// Every render creates a new object — infinite loop!
useEffect(() => {
  doSomething(options);
}, [options]); // options = { page: 1 } created inline

// Fix: declare options outside the component,
// or memoize with useMemo, or list the primitive values
useEffect(() => {
  doSomething({ page });
}, [page]); // primitive — stable comparison
```

## Practice Exercise

The exercise below simulates exactly how React evaluates its dependency array. For each render, compare the values against the previous render and decide whether the effect would run. This exercise builds the intuition that prevents real bugs.

> **Further reading:** [Full Stack Open Part 2](https://fullstackopen.com/en/part2) covers `useEffect` for data fetching extensively, including the cancellation and cleanup patterns used in production applications.
