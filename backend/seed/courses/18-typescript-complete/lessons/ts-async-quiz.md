# Quiz: Async TypeScript

Test your knowledge of typing Promises, async/await, and async patterns in TypeScript.

**Q1. The return type of an `async` function that returns a `string` is:**
- [ ] `string`
- [x] `Promise<string>`
- [ ] `AsyncResult<string>`
- [ ] `string | Promise<string>`

**Q2. Which type correctly expresses "a function that returns a Promise resolving to a User array or null"?**
- [ ] `() => User[] | null`
- [x] `() => Promise<User[] | null>`
- [ ] `async () => User[] | null`
- [ ] `Promise<() => User[] | null>`

**Q3. `Promise.all([p1, p2, p3])` where `p1: Promise<string>`, `p2: Promise<number>`, `p3: Promise<boolean>` resolves to:**
- [ ] `Promise<unknown[]>`
- [ ] `Promise<(string | number | boolean)[]>`
- [x] `Promise<[string, number, boolean]>`
- [ ] `Promise<string & number & boolean>`

**Q4. To type an async generator function that yields numbers, the return type is:**
- [ ] `Generator<number>`
- [ ] `Promise<number[]>`
- [x] `AsyncGenerator<number>`
- [ ] `Iterable<number>`

**Q5. What happens if you `await` a non-Promise value in TypeScript?**
- [ ] Compile error — you can only await Promises
- [x] It is allowed; the value is wrapped in `Promise.resolve()` and unwrapped immediately
- [ ] The value is cast to `unknown`
- [ ] The value is cast to `any`

**Q6. The `Awaited<T>` utility type recursively unwraps Promises. `Awaited<Promise<Promise<string>>>` is:**
- [ ] `Promise<string>`
- [ ] `Promise<Promise<string>>`
- [x] `string`
- [ ] `unknown`
