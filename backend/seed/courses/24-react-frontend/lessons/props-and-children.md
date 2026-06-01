# Props and Children

Props are how parents pass data down to children. They're **read-only** inside the child.

## Receiving props

```tsx
type Props = {
  name: string;
  age: number;
  isAdmin?: boolean;       // optional
};

function User({ name, age, isAdmin = false }: Props) {
  return <div>{name}, {age}, {isAdmin ? "admin" : "user"}</div>;
}
```

Destructuring with defaults is the universal style.

## Passing props

```tsx
<User name="Alice" age={30} />
<User name="Bob" age={42} isAdmin />     // bare attr = true
<User {...userProps} />                   // spread
```

## Don't mutate props

```tsx
function Bad({ users }: { users: User[] }) {
  users.push({...});                     // ❌ mutates parent's array
}

function Good({ users }: { users: User[] }) {
  const next = [...users, {...}];
  // use next; let the parent decide whether to update state
}
```

Props are inputs. To change anything, the parent must re-render with new values (state).

## Children prop

```tsx
type CardProps = { children: React.ReactNode; title: string };

function Card({ title, children }: CardProps) {
  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

<Card title="Hello"><p>body</p></Card>
```

`React.ReactNode` covers strings, numbers, elements, fragments, arrays, null, undefined.

## Function children — render props pattern

```tsx
function Toggle({ children }: { children: (open: boolean) => React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(o => !o)}>toggle</button>
      {children(open)}
    </div>
  );
}

<Toggle>{open => open ? <Body /> : null}</Toggle>
```

Less common since hooks; mostly replaced by custom hooks.

## Composition over prop drilling

If a prop is passed through 4 levels of components untouched, that's **prop drilling**. Two fixes:

1. **Move the consumer closer to the data** — restructure the tree.
2. **Use Context** — for truly global data (theme, current user, locale).

```tsx
const ThemeContext = createContext<"light" | "dark">("light");

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Page />
    </ThemeContext.Provider>
  );
}

function DeepButton() {
  const theme = useContext(ThemeContext);
  return <button className={theme}>Click</button>;
}
```

Don't use Context for things that change often (you'll re-render the whole tree). Use it for app-level constants.

## TypeScript helpers for props

```tsx
type Props = React.ComponentProps<"button">;          // all native button props
type CustomProps = Props & { variant: "primary" };

// extending another component
type LinkProps = React.ComponentProps<typeof Link>;
```

## A common pattern — base + variants

```tsx
type BaseButtonProps = React.ComponentProps<"button"> & {
  variant?: "primary" | "secondary";
};

export function Button({ variant = "primary", className, ...rest }: BaseButtonProps) {
  return (
    <button
      className={`btn btn-${variant} ${className ?? ""}`}
      {...rest}
    />
  );
}

<Button onClick={...} disabled type="submit">Save</Button>
```

Spread the rest of the props to the underlying element — gives users the full HTML API for free.
