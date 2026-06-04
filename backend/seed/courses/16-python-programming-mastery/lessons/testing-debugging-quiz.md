# Quiz: Testing and Debugging

**Q1. In `unittest`, which method checks that two values are equal?**
- [ ] `self.checkEqual(a, b)`
- [x] `self.assertEqual(a, b)`
- [ ] `self.assertSame(a, b)`
- [ ] `assert a == b`

**Q2. `unittest.TestCase.assertRaises` is used to:**
- [ ] Check that a function returns a value
- [x] Verify that a specific exception is raised when calling a function
- [ ] Suppress exceptions during testing
- [ ] Assert that two exceptions are equal

**Q3. In `pdb`, the command `n` means:**
- [ ] "name" — print the current variable
- [x] "next" — execute the current line and stop at the next one
- [ ] "node" — display the call tree
- [ ] "null" — clear the current value

**Q4. Which `pdb` command lets you print the value of a variable `x`?**
- [ ] `var x`
- [ ] `show x`
- [x] `p x`
- [ ] `print(x)` does not work inside pdb

**Q5. `assert` statements should NOT be used for runtime input validation because:**
- [ ] They are too slow
- [x] They are removed entirely when Python runs with the `-O` (optimize) flag
- [ ] They cannot access variable values
- [ ] They only work inside functions

**Q6. A test that passes without actually testing the real behaviour is called a:**
- [ ] Stub test
- [ ] Integration test
- [x] False positive / vacuous test
- [ ] Regression test

**Q7. The `setUp` method in a `unittest.TestCase` subclass runs:**
- [ ] Once before all tests in the class
- [x] Before each individual test method
- [ ] After each individual test method
- [ ] Only if the previous test passed
