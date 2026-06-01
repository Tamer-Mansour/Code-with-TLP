# JSX and Components

React is a library for building UIs out of composable **components**. You write components in JSX — JavaScript with HTML-like syntax — and React reconciles a virtual DOM tree with the real one.

## Hello, JSX

```tsx
function Welcome({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>;
}

function App() {
  return <Welcome name="Alice" />;
}
```

- A component is a function returning JSX.
- Component names start with **uppercase** (`Welcome`); lowercase is interpreted as an HTML tag.
- JSX `{...}` interpolates JavaScript.

## JSX rules

```tsx
// One root element (or fragment)
function Bad() {
  return <div /><div />;       // ❌
}

function Good() {
  return (
    <>
      <div />
      <div />
    </>
  );
}

// className, not class
<div className="card" />

// htmlFor, not for
<label htmlFor="email">Email</label>

// camelCase event handlers
<button onClick={handleClick}>Click</button>

// inline styles are objects, values are camelCase
<div style={{ backgroundColor: "red", fontSize: 14 }} />

// self-closing void elements
<input type="text" />
<br />
```

## Conditional rendering

```tsx
{isLoggedIn && <Profile />}
{isAdmin ? <AdminPanel /> : <UserPanel />}

{users.length === 0 ? (
  <Empty />
) : (
  <UserList users={users} />
)}
```

## Rendering lists

```tsx
<ul>
  {users.map(u => (
    <li key={u.id}>{u.name}</li>
  ))}
</ul>
```

**Always provide a `key`** that's stable and unique among siblings. Index keys (`key={i}`) work in a pinch but break performance and state for reorderable lists.

## A second example

```tsx
type ButtonProps = {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary";
};

export function Button({ label, onClick, variant = "primary" }: ButtonProps) {
  const className = variant === "primary" ? "btn-primary" : "btn-secondary";
  return (
    <button className={className} onClick={onClick}>
      {label}
    </button>
  );
}
```

## Composition

Components compose by including each other:

```tsx
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card">
      <h2>{title}</h2>
      <div>{children}</div>
    </section>
  );
}

<Card title="Profile">
  <Avatar src={url} />
  <Name>{user.name}</Name>
</Card>
```

`children` is a special prop containing whatever's between the open and close tags.

## What goes in a component

A good React component:

- Renders deterministically from props + state.
- Has no side effects during render (those belong in `useEffect`).
- Is small — split when it gets > 100 lines or has > 5 hooks.
- Has a single responsibility — UI for one logical thing.

## File and folder convention

Most codebases use one file per component, `PascalCase.tsx`:

```
src/
  components/
    Button.tsx
    Card.tsx
  features/
    Profile/
      Profile.tsx
      Profile.test.tsx
      useProfile.ts
```

## TSX vs JSX

`.tsx` = TypeScript + JSX. `.jsx` = JavaScript + JSX. Prefer TypeScript for any non-trivial project — the type system catches dozens of UI bugs you'd ship otherwise.
