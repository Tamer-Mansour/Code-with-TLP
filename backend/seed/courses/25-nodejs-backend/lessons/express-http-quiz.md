# Quiz: HTTP and Express

Test your understanding of the Node.js built-in HTTP module, Express routing, middleware, and REST API design.

**Q1. Which built-in Node.js module lets you create an HTTP server without Express?**
- [ ] `node:net`
- [x] `node:http`
- [ ] `node:stream`
- [ ] `node:url`

**Q2. In Express, route parameters (e.g. `/users/:id`) are accessed via:**
- [ ] `req.query.id`
- [ ] `req.body.id`
- [x] `req.params.id`
- [ ] `req.headers.id`

**Q3. What is the correct signature for an Express error-handling middleware?**
- [ ] `(req, res, next) => {}`
- [x] `(err, req, res, next) => {}`
- [ ] `(err, req, res) => {}`
- [ ] `(error, request, response, done) => {}`

**Q4. Which Express method mounts middleware or a router at a specific path prefix?**
- [ ] `app.route()`
- [ ] `app.bind()`
- [x] `app.use()`
- [ ] `app.attach()`

**Q5. What HTTP status code should a successful POST that creates a resource return?**
- [ ] 200
- [x] 201
- [ ] 204
- [ ] 202

**Q6. Express middleware must do one of the following. Which combination is correct?**
- [ ] Call `next()` OR throw an error
- [x] Call `next()` OR send a response (res.send / res.json / etc.)
- [ ] Always call `next()` after sending a response
- [ ] Call both `next()` and `res.json()` in every handler

**Q7. Which package adds security-focused HTTP response headers to an Express app?**
- [ ] `cors`
- [ ] `morgan`
- [x] `helmet`
- [ ] `body-parser`

**Q8. In a REST API, which HTTP verb is used for a partial update of a resource?**
- [ ] PUT
- [ ] POST
- [x] PATCH
- [ ] UPDATE

**Q9. Express.js is:**
- [ ] Part of the Node.js standard library
- [x] A third-party npm package built on top of `node:http`
- [ ] A built-in Node.js module since Node 16
- [ ] Maintained by the Node.js core team

**Q10. The `express.Router()` class is used to:**
- [ ] Speed up route lookups with a trie
- [ ] Handle WebSocket upgrades
- [x] Group related routes into modular, mountable route handlers
- [ ] Automatically generate OpenAPI documentation
