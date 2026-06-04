# Quiz: Testing Node.js APIs

Test your understanding of testing strategies, tools, and best practices for Node.js backend services.

**Q1. Which Node.js built-in flag runs test files without any external dependencies?**
- [ ] `node --jest`
- [x] `node --test`
- [ ] `node --spec`
- [ ] `node run-tests`

**Q2. The `supertest` library is used to:**
- [ ] Generate test data automatically
- [ ] Run E2E browser tests
- [x] Make HTTP requests against an Express app in tests without starting a real server
- [ ] Mock database queries

**Q3. Which testing approach tests a function in isolation, replacing all dependencies with fakes?**
- [ ] Integration testing
- [ ] E2E testing
- [x] Unit testing
- [ ] Smoke testing

**Q4. In Node's built-in test runner, which import provides `equal`, `throws`, and `rejects` assertions?**
- [ ] `import assert from "node:test"`
- [x] `import assert from "node:assert/strict"`
- [ ] `import { expect } from "node:assert"`
- [ ] `import { assert } from "node:util"`

**Q5. What is dependency injection in the context of testability?**
- [ ] Installing test dependencies with npm
- [ ] Injecting test data into a database
- [x] Passing collaborators (db, mailer, etc.) as parameters so tests can substitute fakes
- [ ] Using `require` instead of `import` for mocking

**Q6. Which statement about test coverage is most accurate?**
- [ ] 100% coverage guarantees no bugs
- [ ] Coverage tools are only available with Jest
- [x] High coverage with weak assertions is worse than moderate coverage with strong assertions
- [ ] You should always aim for exactly 80% coverage

**Q7. Where should integration tests (HTTP layer tests) typically be placed?**
- [x] A separate `tests/` directory, not next to source files
- [ ] Directly inside route handler files
- [ ] In `node_modules/tests/`
- [ ] In `package.json` under the `tests` key

**Q8. What is the primary advantage of Vitest over Jest for modern Node.js projects?**
- [ ] It produces better test reports
- [ ] It has more built-in matchers
- [x] It works natively with ESM and TypeScript without extra configuration
- [ ] It runs tests in parallel by default while Jest does not
