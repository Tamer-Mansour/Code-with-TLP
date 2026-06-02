# React with TypeScript

TypeScript makes React code dramatically safer. This lesson covers the most important type patterns you'll use daily.

## Project Setup

The fastest way to start a TypeScript + React project:

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install
```

This generates a project with `.tsx` files and a `tsconfig.json` pre-configured for React.

## Typing Props

Always define an explicit type or interface for props:

```tsx
// Inline type annotation
function Greeting({ name, age }: { name: string; age: number }) {
  return <p>{name} is {age} years old.</p>;
}

// Named type (preferred for reuse/documentation)
type ButtonProps = {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";   // optional with union
  disabled?: boolean;
};

function Button({ label, onClick, variant = "primary", disabled = false }: ButtonProps) {
  return (
    <button
      className={`btn btn--${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
}
```

## Children Types

```tsx
// Any renderable React content
type CardProps = { children: React.ReactNode; title: string };

// Exactly one React element
type WrapperProps = { children: React.ReactElement };

// A render function (render prop pattern)
type ListProps<T> = {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
};
```

## Event Types

Common event handler types:

```tsx
// Mouse events
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => { … };

// Change events
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  console.log(e.target.value);
};

// Form submit
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
};

// Keyboard events
const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === "Enter") { … }
};
```

## useState with Types

TypeScript usually infers the type from the initial value. Annotate explicitly when the type can't be inferred:

```tsx
// Inferred: string
const [name, setName] = useState("");

// Explicit: User | null (can't infer null)
const [user, setUser] = useState<User | null>(null);

// Union type
const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
```

## useRef Types

```tsx
// DOM element ref — starts null, TypeScript knows it might be null
const inputRef = useRef<HTMLInputElement>(null);

// Mutable value ref — starts with a value, no null
const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

// Usage:
inputRef.current?.focus();    // optional chaining handles the null case
```

## Generic Components

Components can be generic when the data type varies:

```tsx
type SelectProps<T extends { id: number; label: string }> = {
  options: T[];
  value: T | null;
  onChange: (item: T) => void;
};

function Select<T extends { id: number; label: string }>({
  options, value, onChange,
}: SelectProps<T>) {
  return (
    <select
      value={value?.id ?? ""}
      onChange={e => {
        const found = options.find(o => String(o.id) === e.target.value);
        if (found) onChange(found);
      }}
    >
      {options.map(o => (
        <option key={o.id} value={o.id}>{o.label}</option>
      ))}
    </select>
  );
}
```

## Discriminated Unions for State

Model complex component state as a discriminated union to make impossible states unrepresentable:

```tsx
type AsyncState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string };

function Component() {
  const [state, setState] = useState<AsyncState<User>>({ status: "idle" });

  if (state.status === "loading") return <Spinner />;
  if (state.status === "error")   return <p>{state.message}</p>;
  if (state.status === "success") return <UserCard user={state.data} />;
  return <button onClick={fetchUser}>Load</button>;
}
```

TypeScript narrows `state` inside each branch — `state.data` is only accessible inside the `"success"` branch.

## Key tsconfig Settings for React

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",          // no need to import React in every file
    "strict": true,              // all strict checks enabled
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

Always use `"strict": true` — it catches null-safety bugs, unused code, and implicit `any` types.

## Summary

| Pattern | Type |
|---------|------|
| Component props | Named type or interface |
| Any renderable content | `React.ReactNode` |
| DOM event handlers | `React.MouseEvent<El>`, `React.ChangeEvent<El>`, etc. |
| Nullable state | `useState<T | null>(null)` |
| DOM refs | `useRef<HTMLElement>(null)` |
| Complex state | Discriminated union |
