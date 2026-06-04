# Quiz: State Management at Scale

**Q1. Which type of state is best handled by React Query (TanStack Query) rather than Redux?**
- [ ] Theme preference (light/dark)
- [ ] Currently authenticated user roles
- [x] Data fetched from a REST API endpoint
- [ ] The currently open modal

**Q2. What does `createSlice` from Redux Toolkit do?**
- [ ] Creates a new React context with built-in reducer support
- [x] Generates action creators and a reducer from a single configuration object
- [ ] Splits the Redux store into multiple independent stores
- [ ] Creates a Zustand store with slice-based naming

**Q3. Redux Toolkit reducers appear to mutate state directly (e.g., `state.items.push(...)`). Why is this safe?**
- [ ] Redux stores a copy of state before every action
- [x] RTK uses the Immer library under the hood, which converts "mutations" to immutable updates
- [ ] Redux Toolkit runs all reducers in a Web Worker
- [ ] JavaScript objects are always copied on assignment

**Q4. In Zustand, what is the purpose of a selector function in `useStore(selector)`?**
- [ ] It filters which actions can be dispatched to the store
- [ ] It transforms the store shape for use with Redux DevTools
- [x] It subscribes the component only to the selected slice, so it re-renders only when that slice changes
- [ ] It replaces the need for `useEffect` for store initialization

**Q5. When should you use `useReducer` instead of `useState`?**
- [ ] When the state is a string or number
- [ ] Whenever you want better performance
- [x] When multiple pieces of state update together based on a typed action, or when the next state depends on complex logic
- [ ] When the component is deeply nested in the tree

**Q6. What is `createAsyncThunk` used for in Redux Toolkit?**
- [ ] Creating synchronous actions that batch multiple state updates
- [ ] Splitting large reducers across multiple files
- [x] Handling async operations (API calls) and automatically dispatching pending/fulfilled/rejected actions
- [ ] Subscribing to WebSocket events from Redux middleware
