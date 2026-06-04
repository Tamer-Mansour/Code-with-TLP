# Quiz: Data Fetching and Async Patterns

**Q1. Why should you return a cleanup function from a `useEffect` that calls `fetch`?**
- [ ] To trigger the next render immediately
- [ ] To cache the response for future calls
- [x] To cancel or ignore the response if the component unmounts or the dependency changes before the fetch completes
- [ ] It is not necessary — `fetch` handles cancellation automatically

**Q2. What does the `queryKey` array in React Query's `useQuery` do?**
- [ ] It controls which component has access to the query
- [x] It serves as the cache key — React Query re-fetches when the key changes
- [ ] It lists the HTTP headers to include in the request
- [ ] It sets the order of parallel queries

**Q3. Which React Query function should you use for data-modifying operations like POST or DELETE?**
- [ ] `useQuery`
- [ ] `useInfiniteQuery`
- [x] `useMutation`
- [ ] `useQueryClient`

**Q4. What is an "optimistic update" in the context of data fetching?**
- [ ] Fetching data before the component mounts to avoid loading states
- [x] Updating the UI immediately as if the server request succeeded, then rolling back if it fails
- [ ] Using `staleTime` to serve cached data without a loading spinner
- [ ] Caching all responses in localStorage

**Q5. What is `staleTime` in React Query?**
- [ ] How long to wait before retrying a failed query
- [ ] The maximum age of the cache before it is garbage-collected
- [x] How long a cached result is considered fresh before React Query re-fetches in the background
- [ ] The timeout for individual network requests

**Q6. What React 18 feature allows components to "suspend" rendering while their data loads, showing a fallback UI?**
- [ ] `useTransition`
- [ ] `useDeferredValue`
- [x] `Suspense` for data fetching
- [ ] `startTransition`
