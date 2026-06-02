# TypeScript with React

TypeScript and React are an excellent combination. You get type-safe props, events, refs, and hooks — catching entire categories of bugs before your code runs.

## Component props

Use an `interface` or `type` alias for props:

```tsx
interface ButtonProps {
  label: string;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

export function Button({ label, variant = "primary", disabled, onClick }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {label}
    </button>
  );
}
```

Optional props (`?`) have `undefined` as part of their type unless you provide a default.

## Children

Use `React.ReactNode` for generic children content:

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
}

export function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}
```

## Typing `useState`

TypeScript usually infers state type from the initial value. Annotate explicitly when the initial value is `null` or a narrower type:

```ts
const [user, setUser] = useState<User | null>(null);
const [count, setCount] = useState(0);                // inferred as number
const [items, setItems] = useState<string[]>([]);
```

## Typing `useRef`

```ts
// DOM element ref
const inputRef = useRef<HTMLInputElement>(null);

// Mutable value (no DOM element)
const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
```

Access via `inputRef.current` — TypeScript knows it can be `null` before mount.

## Typing `useReducer`

Discriminated unions make reducers exhaustive:

```ts
type Action =
  | { type: "increment" }
  | { type: "decrement" }
  | { type: "reset"; payload: number };

type State = { count: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment": return { count: state.count + 1 };
    case "decrement": return { count: state.count - 1 };
    case "reset":     return { count: action.payload };
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0 });
dispatch({ type: "reset", payload: 10 });
```

## Event handlers

React wraps native events — use `React.ChangeEvent`, `React.FormEvent`, etc.:

```ts
function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
  setValue(e.target.value);
}

function handleSubmit(e: React.FormEvent<HTMLFormElement>): void {
  e.preventDefault();
  // ...
}
```

## Generic components

Components can be generic just like functions:

```tsx
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

export function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, i) => (
        <li key={keyExtractor(item)}>{renderItem(item, i)}</li>
      ))}
    </ul>
  );
}

// Usage — T inferred as User
<List
  items={users}
  keyExtractor={u => u.id}
  renderItem={u => <span>{u.name}</span>}
/>
```

## Typing `forwardRef`

```tsx
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  (props, ref) => <input {...props} ref={ref} />
);
```

## Common pitfalls

- `event.target` vs `event.currentTarget` — target is the element clicked, currentTarget is the listener's element. Both are typed differently.
- `as` casts should be a last resort. Prefer narrowing.
- Avoid `any` in prop types; use `unknown` and narrow, or a discriminated union.

TypeScript + React rewards the investment: prop type errors surface immediately, refactoring is safe, and autocomplete in JSX is comprehensive.
