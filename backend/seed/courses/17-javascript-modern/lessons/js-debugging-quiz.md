# Quiz: Error Handling and Debugging

**Q1. What does the following code log?**

```javascript
try {
  null.toString();
} catch (err) {
  console.log(err instanceof TypeError);
}
```

- [ ] `false`
- [x] `true`
- [ ] `undefined`
- [ ] It throws an uncaught error

**Q2. Which statement about `finally` is correct?**

- [ ] `finally` only runs if no error was thrown
- [ ] `finally` only runs if an error was thrown
- [x] `finally` always runs, even if `catch` re-throws an error
- [ ] `finally` runs before `catch`

**Q3. What is printed?**

```javascript
async function test() {
  try {
    const p = fetch("https://bad.url");  // not awaited
  } catch (e) {
    console.log("caught");
  }
}
test();
```

- [x] Nothing is printed — the rejection is NOT caught (missing `await`)
- [ ] `"caught"` is printed
- [ ] A `SyntaxError` is thrown
- [ ] The function returns `undefined`

**Q4. Which is the best practice when catching an unexpected error in a custom handler?**

- [ ] Log it and swallow it silently
- [ ] Convert it to a string and store it
- [x] Re-throw it so it propagates naturally
- [ ] Wrap it in a new error and return `null`

**Q5. Which error type is thrown by `JSON.parse("bad")`?**

- [ ] `TypeError`
- [ ] `RangeError`
- [x] `SyntaxError`
- [ ] `ReferenceError`

**Q6. What is an "unhandled promise rejection"?**

- [ ] A promise that was resolved but the value was `undefined`
- [x] A rejected promise that has no `.catch()` or `try/catch` handling it
- [ ] A promise that timed out
- [ ] Any promise inside an `async` function

**Q7. Which pattern correctly catches errors from an `async` function?**

- [ ] `const data = async getData(); catch(e) {}`
- [ ] `getData().then(d => d).error(e => console.log(e))`
- [x] `try { const data = await getData(); } catch (e) { console.log(e); }`
- [ ] `const data = getData() ?? null;`
