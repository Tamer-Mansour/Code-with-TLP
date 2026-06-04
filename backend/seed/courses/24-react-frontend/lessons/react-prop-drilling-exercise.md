# Prop Drilling and the Context API

Prop drilling is what happens when data must pass through multiple component layers just to reach a deeply nested consumer. It is one of the most common pain points in React codebases, and understanding it drives the need for the Context API, Zustand, and Redux.

## What Is Prop Drilling?

```
App (owns `user`)
  Page        ← receives user, passes it down (doesn't use it)
    Section   ← receives user, passes it down (doesn't use it)
      Panel   ← receives user, passes it down (doesn't use it)
        Avatar ← actually uses user
```

Every intermediate component must accept `user` in its props interface and forward it, even though it has no interest in the data. This is the **prop drilling problem**.

```tsx
// Each intermediate component:
function Page({ user, ...rest }) {
  return <Section user={user} {...rest} />;  // just forwarding
}
```

## Refactoring with Context

The Context API eliminates drilling by making the value available to any descendant directly:

```tsx
const UserContext = createContext<User | null>(null);

function App() {
  const [user] = useState(fetchUser());
  return (
    <UserContext.Provider value={user}>
      <Page /> {/* no user prop needed */}
    </UserContext.Provider>
  );
}

function Avatar() {
  const user = useContext(UserContext); // reaches directly
  return <img src={user?.avatar} />;
}
```

`Page`, `Section`, and `Panel` no longer need to know about `user` at all.

## When Does Drilling Become a Problem?

As a rough guide:

- **1-2 levels deep:** Drilling is fine. Keep props explicit — they are easy to trace.
- **3+ levels deep:** Consider lifting state, compositing children as props, or using Context.
- **Cross-cutting data (auth, theme, locale):** Always use Context or a state library.

## Composition as an Alternative

Sometimes you can avoid both drilling and Context using **component composition**:

```tsx
// Instead of passing user through Page and Section:
function App() {
  const user = ...;
  return (
    <Page>
      <Section>
        <Avatar user={user} /> {/* App passes Avatar directly */}
      </Section>
    </Page>
  );
}
```

The intermediate components accept `children` instead of a `user` prop, never needing to know what's inside.

## Practice Exercise

The exercise below measures prop drilling depth on a component tree. Calculating the exact number of intermediate components that must be touched by a prop is the first step toward deciding whether to refactor.

> **Further reading:** [react.dev — Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context) covers the full Context API with working examples and guidance on when to prefer it over prop drilling.
