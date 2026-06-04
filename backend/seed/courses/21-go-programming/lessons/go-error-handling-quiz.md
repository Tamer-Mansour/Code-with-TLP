# Quiz: Error Handling

**Q1. What is the type of Go's built-in `error`?**
- [ ] A struct with a `message` field
- [ ] A keyword like `nil`
- [x] An interface with a single `Error() string` method
- [ ] A concrete type in the `errors` package

**Q2. Which verb in `fmt.Errorf` wraps an error so it can be unwrapped later?**
- [ ] `%v`
- [ ] `%s`
- [x] `%w`
- [ ] `%e`

**Q3. Why should you use `errors.Is(err, ErrNotFound)` instead of `err == ErrNotFound`?**
- [ ] `==` is not valid for error types
- [x] Wrapping creates a new error value, so `==` fails even when the target is in the chain
- [ ] `errors.Is` is faster
- [ ] They are identical; both work through wrapping

**Q4. `panic()` in Go should be used for:**
- [ ] All unexpected conditions, like exceptions in Java
- [ ] Any error returned from an external API
- [x] Truly unrecoverable programmer errors (e.g., impossible state, out-of-bounds access)
- [ ] Network timeouts and I/O failures

**Q5. When do `defer`-ed calls run?**
- [ ] At the top of the function, before other statements
- [ ] Immediately when the `defer` statement is reached
- [x] When the surrounding function returns, in last-in-first-out order
- [ ] In a background goroutine after the function returns

**Q6. What does `errors.As(err, &target)` do?**
- [ ] Checks if `err` equals `target` by value
- [x] Finds the first error in the chain that matches the type of `target` and assigns it
- [ ] Converts `err` to the type of `target`, panicking on failure
- [ ] Returns the innermost (root cause) error in the chain

**Q7. The idiomatic Go error-handling pattern when calling a function that returns `(T, error)` is:**
- [ ] Wrap everything in a try/catch block
- [ ] Ignore errors unless the function is critical
- [x] Check `if err != nil` immediately after the call and handle or return the error
- [ ] Collect all errors and check them at the end of the function
