# Quiz: React Patterns and Advanced Concepts

**Q1. What does `React.memo` do?**
- [ ] Memoizes a value computed inside a component
- [x] Skips re-rendering a component if its props have not changed (shallow comparison)
- [ ] Caches the return value of an async function
- [ ] Prevents a component from unmounting

**Q2. When should you use `useCallback`?**
- [ ] To cache any expensive calculation
- [x] To keep a function reference stable across renders so it doesn't break `React.memo` on child components
- [ ] To replace `useEffect` for event handlers
- [ ] Whenever you define a function inside a component

**Q3. `useContext` causes a re-render when:**
- [ ] Any state in the application changes
- [x] The context value reference changes (i.e., the Provider receives a new value)
- [ ] A sibling component updates
- [ ] The component's own state changes

**Q4. Which query method should you prefer in React Testing Library?**
- [ ] `getByClassName`
- [ ] `getByTestId`
- [x] `getByRole` — it queries the accessible role
- [ ] `getBySelector`

**Q5. In React Router v6, where do nested child routes render inside their parent layout component?**
- [ ] In a `<div id="root">` at the top of the page
- [ ] Automatically after the last JSX element in the parent
- [x] At the position of the `<Outlet />` component inside the parent
- [ ] They replace the parent entirely

**Q6. Which React Query hook is used for POST/PUT/DELETE operations?**
- [ ] `useQuery`
- [x] `useMutation`
- [ ] `useEffect`
- [ ] `useFetch`

**Q7. What TypeScript type should you use for a prop that accepts any renderable React content (string, element, array, null)?**
- [ ] `React.ReactElement`
- [ ] `JSX.Element`
- [x] `React.ReactNode`
- [ ] `React.FC`
