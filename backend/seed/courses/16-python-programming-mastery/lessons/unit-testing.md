# Unit Testing with unittest

Tests are executable documentation. A well-written test suite tells you exactly what a function is supposed to do and instantly flags when a change breaks it. Python ships `unittest` in the standard library — no install needed.

## Your first test

```python
# math_utils.py
def add(a, b):
    return a + b

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
```

```python
# test_math_utils.py
import unittest
from math_utils import add, is_palindrome

class TestAdd(unittest.TestCase):

    def test_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

    def test_zero(self):
        self.assertEqual(add(0, 10), 10)

class TestPalindrome(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(is_palindrome("racecar"))

    def test_with_spaces(self):
        self.assertTrue(is_palindrome("a man a plan a canal panama"))

    def test_not_palindrome(self):
        self.assertFalse(is_palindrome("hello"))

if __name__ == "__main__":
    unittest.main()
```

Run with `python -m unittest test_math_utils` or `python test_math_utils.py`.

## Common assertion methods

| Method | Checks |
|--------|--------|
| `assertEqual(a, b)` | `a == b` |
| `assertNotEqual(a, b)` | `a != b` |
| `assertTrue(x)` | `bool(x) is True` |
| `assertFalse(x)` | `bool(x) is False` |
| `assertIsNone(x)` | `x is None` |
| `assertIn(a, b)` | `a in b` |
| `assertRaises(Exc, fn, *args)` | `fn(*args)` raises `Exc` |
| `assertAlmostEqual(a, b)` | floats equal to 7 places |

## setUp and tearDown

Run code before and after each test method:

```python
class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = create_test_database()

    def tearDown(self):
        self.db.close()
        delete_test_database()

    def test_insert(self):
        self.db.insert({"id": 1, "name": "Alice"})
        self.assertEqual(self.db.count(), 1)
```

`setUp` is called before each `test_*` method; `tearDown` after. Use `setUpClass` / `tearDownClass` (classmethods) for expensive shared setup.

## Testing exceptions

```python
def test_divide_by_zero(self):
    with self.assertRaises(ZeroDivisionError):
        divide(10, 0)

def test_error_message(self):
    with self.assertRaises(ValueError) as ctx:
        parse_age("-5")
    self.assertIn("negative", str(ctx.exception))
```

## Test discovery

`python -m unittest discover` scans for files matching `test*.py` and runs all `TestCase` subclasses it finds. You can configure the start directory:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Organising tests

```
project/
  src/
    math_utils.py
    strings.py
  tests/
    test_math_utils.py
    test_strings.py
```

Keep tests in a separate `tests/` directory. Name each test file `test_<module>.py` and each test method `test_<what_it_tests>`.

## When to use pytest instead

`unittest` is always available (zero install) and is the right choice for small projects and interview code. For larger projects, `pytest` is the community standard:

- Shorter test syntax (plain `assert` instead of `self.assertEqual`)
- Powerful fixtures and parameterisation
- Rich plugin ecosystem (coverage, async, benchmark)

The concepts — test isolation, one assertion per test, meaningful names — are the same in both.
