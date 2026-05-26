# Quiz: Testing

**Q1. According to the testing pyramid, which type of test should you have the most of?**
- [x] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Manual tests

**Q2. In TDD, what is the correct order of the cycle?**
- [ ] Green → Red → Refactor
- [ ] Refactor → Red → Green
- [x] Red → Green → Refactor
- [ ] Green → Refactor → Red

**Q3. What does 80% code coverage mean?**
- [ ] 80% of bugs have been found by the test suite
- [ ] 80% of features are complete
- [x] 80% of the code lines are executed at least once when the test suite runs
- [ ] 80% of the tests in the suite are currently passing

**Q4. A "Fake" test double is best described as:**
- [ ] A mock that records interactions for later assertion
- [ ] A stub that returns hardcoded values for every call
- [x] A lightweight working implementation used only in tests (e.g., an in-memory database)
- [ ] A spy that wraps the real implementation and records calls

**Q5. Dependency injection improves testability because:**
- [ ] It eliminates the need for any test doubles
- [ ] It makes functions execute faster in production
- [x] It allows tests to supply controlled fake dependencies instead of real external systems
- [ ] It reduces the number of parameters a function needs

**Q6. What is the main risk of overusing mocks in a test suite?**
- [ ] Mocks make tests run slower
- [ ] Mocks require network access
- [x] Tests become tightly coupled to implementation details, breaking whenever the code is refactored even if behaviour is correct
- [ ] Mocks cannot simulate error conditions
