# useContext — Sharing State Without Prop Drilling

**Prop drilling** happens when you pass data through many intermediate components just so a deeply nested component can receive it. `useContext` solves this by making a value available to any component in the tree without explicit prop passing.

## Creating a Context

```tsx
import { createContext, useContext, useState } from "react";

// 1. Create
type Theme = "light" | "dark";
const ThemeContext = createContext<Theme>("light");   // default value

// 2. Provide
function App() {
  const [theme, setTheme] = useState<Theme>("light");
  return (
    <ThemeContext.Provider value={theme}>
      <button onClick={() => setTheme(t => t === "light" ? "dark" : "light")}>
        Toggle
      </button>
      <Page />
    </ThemeContext.Provider>
  );
}

// 3. Consume — anywhere in the subtree
function Card() {
  const theme = useContext(ThemeContext);
  return <div className={`card card--${theme}`}>…</div>;
}
```

Any component inside `<ThemeContext.Provider>` can call `useContext(ThemeContext)` without any parent having to pass `theme` as a prop.

## Context + useReducer Pattern

For non-trivial shared state, pair context with `useReducer`:

```tsx
type User = { id: number; name: string } | null;
type AuthState = { user: User; loading: boolean };
type AuthAction =
  | { type: "login"; user: User }
  | { type: "logout" }
  | { type: "loading" };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "login":   return { user: action.user, loading: false };
    case "logout":  return { user: null, loading: false };
    case "loading": return { ...state, loading: true };
  }
}

type AuthCtx = { state: AuthState; dispatch: React.Dispatch<AuthAction> };
const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, { user: null, loading: false });
  return <AuthContext.Provider value={{ state, dispatch }}>{children}</AuthContext.Provider>;
}

// Custom hook — throws if used outside provider
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
```

Consumer components simply call `useAuth()`:

```tsx
function ProfileButton() {
  const { state, dispatch } = useAuth();
  if (state.user) {
    return <button onClick={() => dispatch({ type: "logout" })}>{state.user.name}</button>;
  }
  return <button onClick={() => dispatch({ type: "loading" })}>Log in</button>;
}
```

## Performance Considerations

Every component that calls `useContext(MyContext)` re-renders whenever the context **value** changes. To prevent unnecessary renders:

1. **Split contexts** — put frequently-changing data (e.g., cursor position) in its own context, separate from stable data (e.g., theme).
2. **Memoize the value** — use `useMemo` to avoid creating a new object reference on every parent render:

```tsx
const value = useMemo(() => ({ state, dispatch }), [state]);
<AuthContext.Provider value={value}>…</AuthContext.Provider>
```

3. **Use selector hooks** — if the context has many fields, expose small hooks that read only what's needed, and wrap consumers in `React.memo`.

## When NOT to Use Context

| Situation | Better tool |
|-----------|-------------|
| Deeply nested but few components | Pass props with composition (`children`) |
| Server-authoritative data | React Query / SWR |
| Large, complex client state | Zustand, Redux Toolkit |
| Component-local state | `useState` |

Context is ideal for **medium-scope, slowly-changing** data: auth, theme, locale, feature flags.

## Summary

- `createContext` + `Provider` sets up a shareable channel.
- `useContext` consumes it in any descendant without prop drilling.
- Combine with `useReducer` for structured updates.
- Split and memoize to avoid over-rendering.
