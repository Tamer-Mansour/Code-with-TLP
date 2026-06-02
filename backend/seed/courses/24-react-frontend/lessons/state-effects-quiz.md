# Quiz: State and Effects

**Q1. Which hook should you use when new state depends on the previous value?**
- [ ] `useState` with direct assignment
- [x] `useState` with a functional updater: `setCount(c => c + 1)`
- [ ] `useEffect` inside the setter
- [ ] `useRef`

**Q2. When does `useEffect` with an empty dependency array `[]` run?**
- [ ] On every render
- [x] Once after the first render (mount)
- [ ] Only when the component unmounts
- [ ] Never — an empty array disables the effect

**Q3. You fetch user data inside `useEffect`. What should you return from the effect to avoid a memory leak when the component unmounts?**
- [ ] The fetched data
- [ ] `null`
- [x] A cleanup function that aborts the fetch or sets a flag
- [ ] Nothing — `useEffect` cleans up automatically

**Q4. Which of these will cause a re-render?**
- [ ] Mutating an object stored in state: `state.name = "Bob"; setState(state);`
- [x] Replacing with a new object: `setState({ ...state, name: "Bob" })`
- [ ] Assigning a new value to a `useRef` variable
- [ ] Calling `console.log` inside the component body

**Q5. What is the correct way to avoid stale closure bugs when incrementing a counter in a timeout?**
- [ ] `setTimeout(() => setCount(count + 1), 1000)`
- [x] `setTimeout(() => setCount(c => c + 1), 1000)`
- [ ] `useRef` to store count and update it directly
- [ ] Re-create the timeout on every render

**Q6. When is `useReducer` preferable to `useState`?**
- [ ] When the state is a single boolean
- [ ] When the update is synchronous
- [x] When several state values change together based on an action type
- [ ] When you want to avoid re-renders
