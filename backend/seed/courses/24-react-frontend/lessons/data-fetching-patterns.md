# Data Fetching Patterns

Nearly every React application fetches data from an API. This lesson covers the patterns from manual `useEffect` fetching all the way to production-grade caching libraries.

## Manual Fetch with useEffect

The baseline pattern — direct `fetch` inside `useEffect`:

```tsx
import { useState, useEffect } from "react";

type User = { id: number; name: string; email: string };

function UserProfile({ userId }: { userId: number }) {
  const [user, setUser]       = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;       // prevent setting state after unmount
    setLoading(true);
    setError(null);

    fetch(`/api/users/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => { if (!cancelled) setUser(data); })
      .catch(err  => { if (!cancelled) setError(err.message); })
      .finally(()  => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };    // cleanup
  }, [userId]);

  if (loading) return <p>Loading…</p>;
  if (error)   return <p>Error: {error}</p>;
  if (!user)   return null;
  return <div>{user.name} — {user.email}</div>;
}
```

This pattern is correct but verbose. It grows further when you need caching, pagination, or mutations.

## A Custom useFetch Hook

Extract the fetch logic into a reusable hook:

```tsx
function useFetch<T>(url: string) {
  const [data, setData]       = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(r => r.json())
      .then(d  => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch(e => { if (!cancelled) { setError(e.message); setLoading(false); } });
    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}

// Usage:
const { data: user, loading, error } = useFetch<User>(`/api/users/${userId}`);
```

## React Query (TanStack Query)

For production, **React Query** handles caching, background refetching, stale-while-revalidate, deduplication, and much more:

```bash
npm install @tanstack/react-query
```

```tsx
import { useQuery, QueryClient, QueryClientProvider } from "@tanstack/react-query";

// 1. Create and provide a client (once, at the root)
const queryClient = new QueryClient();

function Root() {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
}

// 2. Query data in any component
function UserProfile({ userId }: { userId: number }) {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
    staleTime: 60_000,          // keep fresh for 1 minute
  });

  if (isLoading) return <p>Loading…</p>;
  if (error)     return <p>Error fetching user</p>;
  return <div>{user.name}</div>;
}
```

### Key React Query features

| Feature | Description |
|---------|-------------|
| `queryKey` | Cache key — re-fetches when key changes |
| `staleTime` | How long to consider data fresh (ms) |
| `refetchOnWindowFocus` | Auto-refresh when tab is re-focused |
| `useMutation` | POST/PUT/DELETE with optimistic updates |
| `invalidateQueries` | Invalidate cache to trigger re-fetch |

## SWR (Stale-While-Revalidate)

A lighter alternative by Vercel:

```tsx
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then(r => r.json());

function UserProfile({ userId }: { userId: number }) {
  const { data, error, isLoading } = useSWR(`/api/users/${userId}`, fetcher);
  // ...
}
```

SWR is minimal and great for read-heavy UIs; React Query offers richer features for complex mutations.

## Choosing the Right Approach

| Approach | Best for |
|----------|----------|
| Raw `useEffect` | Learning, one-off fetches |
| Custom hook | Small apps, minimal deps |
| React Query | Most production React apps |
| SWR | Next.js projects, Vercel-hosted apps |

The manual pattern teaches the fundamentals; use a library in real projects to avoid reinventing caching, deduplication, and error boundaries.
