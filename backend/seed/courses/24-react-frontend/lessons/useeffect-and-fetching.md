# useEffect and Data Fetching

`useEffect` runs side effects — subscriptions, timers, DOM measurements, data fetching — after React has updated the DOM.

## The shape

```tsx
useEffect(() => {
  // side effect
  return () => {
    // cleanup (runs before next effect, and on unmount)
  };
}, [dep1, dep2]);
```

The dependency array decides **when** the effect re-runs:

- `[]` — once, after mount.
- `[a, b]` — when `a` or `b` changes between renders.
- No array — every render (rare; usually wrong).

## A first effect

```tsx
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

Subscribe + always clean up. Forgetting the cleanup leaks timers, listeners, or subscriptions.

## Data fetching

The naive form:

```tsx
function UserCard({ id }: { id: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/users/${id}`)
      .then(r => r.json())
      .then(data => { if (!cancelled) setUser(data); })
      .catch(e => { if (!cancelled) setError(e.message); });
    return () => { cancelled = true; };
  }, [id]);

  if (error) return <Error msg={error} />;
  if (!user) return <Loading />;
  return <Profile user={user} />;
}
```

Notice the **cancellation flag**. Without it, an old fetch returning after `id` changed could overwrite the newer data — a race condition.

## Reach for a library

In real apps you almost never write fetch-in-useEffect by hand. Use one of:

- **TanStack Query (React Query)** — declarative data fetching with caching, retries, dedupe, mutations.
- **SWR** — similar, smaller surface area.
- **Apollo Client** for GraphQL.

```tsx
import { useQuery } from "@tanstack/react-query";

function UserCard({ id }: { id: string }) {
  const { data: user, error, isPending } = useQuery({
    queryKey: ["user", id],
    queryFn: () => fetch(`/api/users/${id}`).then(r => r.json()),
  });

  if (error) return <Error msg={error.message} />;
  if (isPending) return <Loading />;
  return <Profile user={user} />;
}
```

Caching, automatic deduplication, retry, background refetching — all handled.

## The dependency array — strict mode

React's exhaustive-deps lint rule will flag any variable from the closure that's used inside the effect but not in the array. Trust it. When you "know" a missing dep is fine, you usually have a stale-closure bug waiting.

## Common effect patterns

### Subscribe to something

```tsx
useEffect(() => {
  const handler = () => setSize({ w: innerWidth, h: innerHeight });
  window.addEventListener("resize", handler);
  return () => window.removeEventListener("resize", handler);
}, []);
```

### Sync URL with state

```tsx
useEffect(() => {
  const url = new URL(window.location.href);
  url.searchParams.set("q", query);
  window.history.replaceState(null, "", url);
}, [query]);
```

### Focus an input on mount

```tsx
const ref = useRef<HTMLInputElement>(null);
useEffect(() => { ref.current?.focus(); }, []);
```

## Don't use effects for derived state

```tsx
// ❌ unnecessary
const [fullName, setFullName] = useState("");
useEffect(() => { setFullName(`${first} ${last}`); }, [first, last]);

// ✓ derive
const fullName = `${first} ${last}`;
```

A `useEffect` that just sets state from props is a re-render loop in disguise.

## React 18 — Strict Mode

In dev, React intentionally runs effects twice on mount. Helps catch missing cleanups. Don't suppress; fix the effect.
