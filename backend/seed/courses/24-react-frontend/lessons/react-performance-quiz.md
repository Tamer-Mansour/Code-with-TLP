# Quiz: Performance Optimization

**Q1. By default, when a parent component re-renders, what happens to its child components?**
- [ ] Only children whose props changed re-render
- [ ] Only children that call `useState` re-render
- [x] All child components re-render, regardless of whether their props changed
- [ ] Children re-render only if they call `useEffect`

**Q2. What does `React.memo` do?**
- [ ] Caches the result of an expensive calculation inside a component
- [x] Wraps a component so it skips re-rendering when its props are shallowly equal to the previous render's props
- [ ] Memoizes the component's JSX output in a string cache
- [ ] Prevents the component from ever re-rendering

**Q3. Why do you need `useCallback` to make `React.memo` effective when passing a callback prop?**
- [ ] `useCallback` converts the function into a primitive value
- [ ] Without it, the function runs on every render twice
- [x] Without `useCallback`, a new function reference is created on every render, so the shallow prop comparison in `React.memo` always sees a changed prop
- [ ] `React.memo` only works with `useCallback`-wrapped callbacks

**Q4. `useMemo` should be used when:**
- [ ] You want to prevent all re-renders of a component
- [x] You have an expensive computation whose result should only be recalculated when specific dependencies change
- [ ] You are wrapping a callback function to stabilize its reference
- [ ] You want to cache API responses

**Q5. Which tool is the correct way to identify which components are re-rendering unnecessarily?**
- [ ] `console.log` inside every component
- [ ] The browser Network tab
- [x] The React DevTools Profiler
- [ ] Lighthouse performance audit

**Q6. What is code splitting in the context of React performance?**
- [ ] Dividing a component into smaller sub-components
- [ ] Splitting the CSS bundle from the JS bundle
- [x] Lazily loading parts of the JavaScript bundle only when they are needed, using `React.lazy` and `Suspense`
- [ ] Breaking the app into multiple independent React roots
