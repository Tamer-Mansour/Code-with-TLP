# State Management at Scale

As React applications grow, local component state (`useState`) stops being enough. Data needs to be shared across distant parts of the component tree, synchronized with a server, and kept consistent across navigation. This lesson maps out the state management landscape.

## The Four Categories of State

Before choosing a tool, identify what kind of state you have:

| Category | Examples | Best tool |
|----------|----------|-----------|
| **Local UI state** | Modal open, selected tab, form input value | `useState` / `useReducer` |
| **Shared app state** | Current user, theme, shopping cart | Context + useReducer or Zustand |
| **Server/async state** | API responses, lists, user profiles | TanStack Query (React Query) |
| **URL/navigation state** | Active filter, current page, selected item | React Router search params |

**A common mistake** is putting server data (API responses) in Redux or Context. This forces you to manage loading, error, caching, and invalidation by hand — problems React Query solves for free.

## Context API — Built-In, Good Enough for Many Apps

The Context API is already in React and requires no dependencies. Pair it with `useReducer` for structured updates:

```tsx
const CartContext = createContext(null);

function CartProvider({ children }) {
  const [items, dispatch] = useReducer(cartReducer, []);
  return (
    <CartContext.Provider value={{ items, dispatch }}>
      {children}
    </CartContext.Provider>
  );
}
```

**Limit:** Every consumer re-renders when the context value changes. For high-frequency updates (mouse position, scroll), context is the wrong tool.

## Zustand — Lightweight Global Store

Zustand is a minimal state library with no boilerplate and excellent performance:

```tsx
import { create } from 'zustand';

const useCartStore = create((set) => ({
  items: [],
  addItem: (item) => set((s) => ({ items: [...s.items, item] })),
  removeItem: (id) => set((s) => ({ items: s.items.filter(i => i.id !== id) })),
}));

function CartIcon() {
  const count = useCartStore((s) => s.items.length); // selector — only re-renders on count change
  return <span>{count}</span>;
}
```

Zustand stores live outside the React tree — no Provider needed. Selectors prevent unnecessary re-renders.

## Redux Toolkit — For Large, Complex Apps

Redux Toolkit (RTK) is the modern way to write Redux. It eliminates the old boilerplate:

```tsx
import { createSlice, configureStore } from '@reduxjs/toolkit';

const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [] },
  reducers: {
    addItem: (state, action) => { state.items.push(action.payload); },   // Immer under the hood
    removeItem: (state, action) => {
      state.items = state.items.filter(i => i.id !== action.payload);
    },
  },
});

export const { addItem, removeItem } = cartSlice.actions;
const store = configureStore({ reducer: { cart: cartSlice.reducer } });

// In components:
const items = useSelector((s) => s.cart.items);
const dispatch = useDispatch();
dispatch(addItem({ id: 1, name: 'Widget' }));
```

RTK uses **Immer** internally so you can write "mutating" reducer logic that is actually immutable.

## Async State with Redux Toolkit

Use `createAsyncThunk` for API calls that need to live in Redux:

```tsx
const fetchUser = createAsyncThunk('users/fetch', async (id) => {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
});

// Handle in a slice's extraReducers:
builder
  .addCase(fetchUser.pending,   (s) => { s.loading = true; })
  .addCase(fetchUser.fulfilled, (s, a) => { s.user = a.payload; s.loading = false; })
  .addCase(fetchUser.rejected,  (s, a) => { s.error = a.error.message; s.loading = false; });
```

That said, **React Query is almost always the better choice for server state** — it handles caching, retries, and background refresh automatically.

## Decision Guide

```
Is the state derived from a server? → React Query
Is the state used in only one component? → useState
Is it shared by 2-3 nearby components? → Lift state + props
Is it cross-cutting (auth, theme, locale)? → Context
Large app, many features, team project? → Redux Toolkit or Zustand
Want minimal setup with good perf? → Zustand
```

> **Further reading:** [Full Stack Open Part 6](https://fullstackopen.com/en/part6) covers Redux Toolkit and React Query together with real-world exercises that show exactly when each tool fits.
