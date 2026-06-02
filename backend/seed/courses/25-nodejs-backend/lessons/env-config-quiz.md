# Quiz: Database, Testing, and Deployment

Check your understanding of the database integration, testing, and deployment lessons.

**Q1. Which SQL placeholder style does the `pg` (node-postgres) driver use for parameterized queries?**
- [ ] `?` (question mark)
- [x] `$1`, `$2`, `$3` (numbered)
- [ ] `:name` (named)
- [ ] `%s` (printf-style)

**Q2. In a connection pool, why should you always call `client.release()` in a `finally` block?**
- [ ] To commit the transaction
- [x] To return the connection to the pool so it can be reused
- [ ] To close the database
- [ ] To flush pending queries

**Q3. Which Supertest import allows you to test an Express app without calling `app.listen()`?**
- [ ] `import { listen } from "supertest"`
- [x] `import request from "supertest"` then `request(app).get(...)`
- [ ] `import { mount } from "supertest"`
- [ ] `import { agent } from "supertest"` then `agent.start(app)`

**Q4. What HTTP status code should a `/health` endpoint return when the service cannot reach the database?**
- [ ] 200
- [ ] 404
- [ ] 500
- [x] 503

**Q5. In a Dockerfile, which command installs exact versions from `package-lock.json` without modifying it?**
- [ ] `npm install`
- [x] `npm ci`
- [ ] `npm install --frozen`
- [ ] `npm install --exact`

**Q6. When a Node process receives `SIGTERM`, what is the correct response for graceful shutdown?**
- [ ] Call `process.exit(1)` immediately
- [ ] Ignore the signal and keep serving requests
- [x] Stop accepting new connections, finish in-flight requests, then exit 0
- [ ] Restart the process

**Q7. Which Node.js flag runs the built-in test runner (no external library needed)?**
- [ ] `node --jest`
- [x] `node --test`
- [ ] `node --spec`
- [ ] `node --mocha`
