# Custom Hooks

A **custom hook** is a function that starts with `use` and may call other hooks. It's the canonical way to share logic between components — no HOCs, no render props.

## A first custom hook

```tsx
function useCounter(initial = 0) {
  const [count, setCount] = useState(initial);
  const inc = useCallback(() => setCount(c => c + 1), []);
  const dec = useCallback(() => setCount(c => c - 1), []);
  const reset = useCallback(() => setCount(initial), [initial]);
  return { count, inc, dec, reset };
}

function Counter() {
  const { count, inc, dec, reset } = useCounter(10);
  ...
}
```

Custom hooks compose the built-in ones; the rules of hooks (call from the top of a component or hook, in the same order each render) still apply.

## useLocalStorage

```tsx
function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : initial;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

const [theme, setTheme] = useLocalStorage("theme", "light");
```

State that survives reloads, in 10 lines.

## useDebounced

```tsx
function useDebounced<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(id);
  }, [value, ms]);
  return debounced;
}

const query = useDebounced(input, 300);
// fire search only when user stops typing for 300ms
```

## useOnClickOutside

```tsx
function useOnClickOutside(ref: React.RefObject<HTMLElement>, handler: () => void) {
  useEffect(() => {
    const listener = (e: MouseEvent) => {
      if (!ref.current || ref.current.contains(e.target as Node)) return;
      handler();
    };
    document.addEventListener("mousedown", listener);
    return () => document.removeEventListener("mousedown", listener);
  }, [ref, handler]);
}

function Dropdown() {
  const ref = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  useOnClickOutside(ref, () => setOpen(false));
  return <div ref={ref}>...</div>;
}
```

## usePrevious

```tsx
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current;
}
```

## Rules of hooks

1. Only call hooks at the **top level** — not inside conditionals, loops, or nested functions.
2. Only call hooks from **React components** or **other custom hooks**.

ESLint's `react-hooks/rules-of-hooks` and `react-hooks/exhaustive-deps` rules enforce both.

## When to extract a hook

- The same useState + useEffect pattern appears in 2+ components.
- Some "logic" is interfering with the JSX readability of a component.
- You want to test the logic separately from the UI.

Don't extract a hook for a one-off snippet — that's just more layers without payoff.

## A note on patterns

Avoid "general-purpose" hooks like `useThings` that take a config and do everything. Hooks like `useUser`, `useSearchResults`, `useShoppingCart` — purpose-specific, with named outputs — are easier to read and refactor.
