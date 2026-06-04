# Quiz: Asynchronous JavaScript

**Q1. In what order does this code print?**
```javascript
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
```
- [ ] A, B, C, D
- [ ] A, D, B, C
- [x] A, D, C, B
- [ ] A, C, D, B

**Q2. What is the microtask queue used for?**
- [ ] `setTimeout` and `setInterval` callbacks
- [ ] DOM click event handlers
- [x] Promise `.then` / `.catch` / `.finally` callbacks and `queueMicrotask`
- [ ] `requestAnimationFrame` callbacks

**Q3. Does JavaScript use multiple threads when you `await` a fetch call?**
- [ ] Yes, the fetch runs on a background thread
- [x] No, JavaScript is single-threaded. `await` suspends the current async function and returns control to the event loop; the network I/O is handled by the browser/Node outside the JS thread
- [ ] Yes, async/await automatically spawns a Web Worker
- [ ] It depends on whether you use `async/await` or `.then()`

**Q4. What does `Promise.allSettled` do differently from `Promise.all`?**
- [ ] `Promise.allSettled` is faster
- [ ] They are identical
- [x] `Promise.all` rejects as soon as any promise rejects; `Promise.allSettled` always waits for all promises and returns their outcomes (fulfilled or rejected)
- [ ] `Promise.allSettled` only works with arrays of exactly two promises

**Q5. What happens if you `throw` inside an `async` function?**
- [ ] The error is silently swallowed
- [ ] It terminates the Node.js process
- [x] The returned Promise is rejected with that error, catchable via `.catch()` or `try/catch` around `await`
- [ ] The error is converted to a string and returned

**Q6. What is "callback hell" and what solves it?**
- [ ] An error caused by calling a function too many times; solved by memoization
- [x] Deeply nested callbacks that become unreadable; solved by Promises and async/await
- [ ] Callbacks that run in the wrong order; solved by setTimeout
- [ ] Functions that call themselves recursively; solved by tail call optimization

**Q7. `Promise.race([p1, p2, p3])` resolves or rejects with:**
- [ ] The result of whichever promise takes the longest
- [ ] An array of all results
- [x] The result of whichever promise settles first (whether fulfilled or rejected)
- [ ] Only fulfilled values; rejected promises are ignored
