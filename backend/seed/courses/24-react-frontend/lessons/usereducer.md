# useReducer — Complex State Logic

`useReducer` is an alternative to `useState` for managing state that involves multiple sub-values or complex update logic. It follows the same reducer pattern popularised by Redux.

## When to Prefer useReducer

| Situation | Prefer |
|-----------|--------|
| Single primitive value | `useState` |
| Independent simple values | `useState` |
| Multiple values that change together | `useReducer` |
| Next state depends on action type | `useReducer` |
| Complex update logic you want to test in isolation | `useReducer` |

## Basic Pattern

```tsx
import { useReducer } from "react";

type State = { count: number };
type Action = { type: "increment" } | { type: "decrement" } | { type: "reset" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment": return { count: state.count + 1 };
    case "decrement": return { count: state.count - 1 };
    case "reset":     return { count: 0 };
    default:          return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });
  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: "increment" })}>+</button>
      <button onClick={() => dispatch({ type: "decrement" })}>−</button>
      <button onClick={() => dispatch({ type: "reset" })}>Reset</button>
    </div>
  );
}
```

`useReducer(reducer, initialState)` returns `[state, dispatch]`.

- **`state`** — the current state value.
- **`dispatch(action)`** — sends an action to the reducer, which computes and returns the next state, triggering a re-render.

## Real-World Example: Shopping Cart

```tsx
type Product = { id: number; name: string; price: number };
type CartItem = Product & { qty: number };

type CartState = { items: CartItem[] };
type CartAction =
  | { type: "add"; product: Product }
  | { type: "remove"; id: number }
  | { type: "clear" };

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case "add": {
      const existing = state.items.find(i => i.id === action.product.id);
      if (existing) {
        return {
          items: state.items.map(i =>
            i.id === action.product.id ? { ...i, qty: i.qty + 1 } : i
          ),
        };
      }
      return { items: [...state.items, { ...action.product, qty: 1 }] };
    }
    case "remove":
      return { items: state.items.filter(i => i.id !== action.id) };
    case "clear":
      return { items: [] };
  }
}
```

Each action type has a clearly defined shape (discriminated union). The reducer is a **pure function** — same inputs always produce the same output, no side effects — so you can unit-test it without mounting any React component.

## Testing a Reducer

Because a reducer is a pure function, testing is straightforward:

```ts
import { cartReducer } from "./cartReducer";

test("add new item", () => {
  const state = cartReducer({ items: [] }, { type: "add", product: { id: 1, name: "Book", price: 10 } });
  expect(state.items).toHaveLength(1);
  expect(state.items[0].qty).toBe(1);
});

test("increment qty of existing item", () => {
  const initial = { items: [{ id: 1, name: "Book", price: 10, qty: 2 }] };
  const next = cartReducer(initial, { type: "add", product: { id: 1, name: "Book", price: 10 } });
  expect(next.items[0].qty).toBe(3);
});
```

## Initialising State Lazily

Pass a third `init` argument to compute the initial state from the second argument:

```tsx
function init(initialCount: number) {
  return { count: initialCount };
}

function Counter({ initialCount }: { initialCount: number }) {
  const [state, dispatch] = useReducer(reducer, initialCount, init);
  // ...
}
```

This is useful when the initial state is expensive to compute or when you want to re-use the init logic for a "reset" action.

## useReducer + Context for Global State

Combine `useReducer` with `useContext` to share state across a tree without a third-party library:

```tsx
const CartContext = createContext<{ state: CartState; dispatch: React.Dispatch<CartAction> } | null>(null);

function CartProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });
  return <CartContext.Provider value={{ state, dispatch }}>{children}</CartContext.Provider>;
}
```

Any child can consume the context with `useContext(CartContext)` and dispatch actions without prop drilling.

## Summary

- `useReducer` keeps complex update logic in one place — the reducer function.
- Discriminated union action types make the logic self-documenting.
- Pure reducers are trivial to unit-test.
- Pair with `useContext` for lightweight global state management.
