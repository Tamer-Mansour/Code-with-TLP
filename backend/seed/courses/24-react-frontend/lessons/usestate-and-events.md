# useState and Events

`useState` is the simplest **hook** — it gives a component a piece of state that survives renders.

## The basics

```tsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  );
}
```

`useState(initial)` returns `[current, setter]`. Calling the setter schedules a re-render with the new value.

## Lazy initial state

If computing the initial value is expensive:

```tsx
const [items, setItems] = useState(() => loadFromLocalStorage());
```

The function only runs on the first render.

## Functional updates

When the new state depends on the previous:

```tsx
setCount(c => c + 1);
```

Use the function form whenever the update depends on the current value — avoids stale-closure bugs and works correctly with batched updates.

## State is immutable from React's perspective

You **never** mutate state in place — React diff'd by reference:

```tsx
const [user, setUser] = useState({ name: "Alice", age: 30 });

user.age = 31; setUser(user);            // ❌ same reference, no re-render
setUser({ ...user, age: 31 });           // ✓ new object
setUser(u => ({ ...u, age: u.age + 1 }));  // ✓ functional form
```

For arrays:

```tsx
setItems([...items, newItem]);
setItems(items.filter(x => x.id !== id));
setItems(items.map(x => x.id === id ? { ...x, ...patch } : x));
```

For deeply nested state, **Immer** simplifies:

```tsx
import { useImmer } from "use-immer";
const [state, setState] = useImmer({ deeply: { nested: { x: 1 } } });
setState(draft => { draft.deeply.nested.x = 2; });   // mutate the draft
```

## Multiple state pieces

```tsx
const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [age, setAge] = useState(0);
```

Or one object if they always change together:

```tsx
const [form, setForm] = useState({ name: "", email: "", age: 0 });
const update = (k, v) => setForm(f => ({ ...f, [k]: v }));
```

## Events

JSX uses camelCase event names:

```tsx
<button onClick={handleClick} />
<input onChange={e => setName(e.target.value)} />
<form onSubmit={handleSubmit} />
```

The handler receives a **SyntheticEvent** — a cross-browser wrapper. Common access:

```tsx
function handleClick(e: React.MouseEvent<HTMLButtonElement>) {
  e.preventDefault();
  e.stopPropagation();
  console.log(e.currentTarget);
}

function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value);
}
```

## Controlled vs uncontrolled inputs

```tsx
// Controlled — value lives in React state
<input value={name} onChange={e => setName(e.target.value)} />

// Uncontrolled — value lives in the DOM
const inputRef = useRef<HTMLInputElement>(null);
<input ref={inputRef} defaultValue="hi" />
// access via inputRef.current?.value
```

Controlled is the default for most forms. Uncontrolled (with refs) is useful for very large forms or integration with non-React libraries.

## Batching

React batches state updates inside event handlers — multiple `setX` calls produce **one** re-render:

```tsx
function handleClick() {
  setA(1);     // no render yet
  setB(2);     // no render yet
  setC(3);     // one render at the end
}
```

In React 18+, batching also happens in promises, setTimeout, and native event handlers.
