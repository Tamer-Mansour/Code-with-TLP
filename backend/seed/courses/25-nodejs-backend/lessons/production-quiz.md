# Quiz: Production Concerns

Test your understanding of validation, error handling, security, and logging in Node.js APIs.

**Q1. Which Zod method returns `{ success, data }` instead of throwing on failure?**
- [ ] `z.schema.parse(data)`
- [x] `z.schema.safeParse(data)`
- [ ] `z.schema.validate(data)`
- [ ] `z.schema.check(data)`

**Q2. Express error-handling middleware is identified by having how many arguments?**
- [ ] 2
- [ ] 3
- [x] 4
- [ ] 5

**Q3. What does `express-rate-limit` use by default to store request counters?**
- [x] In-memory (process memory)
- [ ] Redis
- [ ] SQLite
- [ ] A temporary file

**Q4. Which npm package sets security-related HTTP response headers like `X-Frame-Options` and `Content-Security-Policy`?**
- [ ] `cors`
- [ ] `body-parser`
- [x] `helmet`
- [ ] `morgan`

**Q5. When a route handler `async` function throws in Express 4, what must you do to reach the error middleware?**
- [ ] Nothing — Express 4 handles async errors automatically
- [x] Call `next(err)` inside a try/catch
- [ ] Use `res.status(500).end()`
- [ ] Re-throw the error with `throw err`

**Q6. In Pino, which log level should be used when an error requires immediate developer attention?**
- [ ] `warn`
- [x] `error`
- [ ] `info`
- [ ] `trace`

**Q7. Which CORS configuration is insecure for an API that uses authentication cookies?**
- [ ] `cors({ origin: "https://myapp.com" })`
- [x] `cors({ origin: "*" })`
- [ ] `cors({ origin: ["https://app.com", "https://admin.app.com"] })`
- [ ] `cors({ credentials: true, origin: "https://myapp.com" })`

**Q8. What is the correct place to register an Express error-handling middleware?**
- [ ] Before any routes
- [ ] At the top of app.js
- [x] After all routes and regular middleware
- [ ] Inside each route handler
