# Pre vs Post Increment Overloads

The increment (`++`) and decrement (`--`) operators each have two forms: **prefix** and **postfix**. C++ uses a dummy `int` parameter to distinguish the postfix form at compile time.

## Signature Convention

```cpp
struct Counter {
    int value;

    // Prefix  ++c  — increments, returns the NEW value by reference
    Counter& operator++() {
        ++value;
        return *this;
    }

    // Postfix  c++  — increments, returns the OLD value by value
    Counter operator++(int) {        // the int is a dummy tag; never used
        Counter old = *this;         // save current state
        ++(*this);                   // delegate to prefix
        return old;                  // return saved (old) value
    }
};
```

The same pattern applies to `--`:

```cpp
Counter& operator--()    { --value; return *this; }
Counter  operator--(int) { Counter old = *this; --(*this); return old; }
```

## Why Postfix Returns by Value

Postfix must return the **value before the increment**. That value is a temporary that no longer exists after the function returns, so returning a reference would be undefined behaviour. It must return by value.

## Why Prefix Is Faster

- Prefix: one operation — modify and return `*this`.
- Postfix: copy construction + modification + destruction of the old copy.

For primitive types the compiler optimises this away, but for heavy objects (iterators, big integers) the extra copy is real.

```cpp
// Prefer ++it over it++ in loops when you don't need the old value
for (auto it = container.begin(); it != container.end(); ++it) { ... }
```

## Worked Example: Iterator-Style Class

```cpp
class RangeIterator {
    int current;
public:
    explicit RangeIterator(int v) : current(v) {}

    int operator*() const { return current; }

    // Prefix ++
    RangeIterator& operator++() {
        ++current;
        return *this;
    }

    // Postfix ++
    RangeIterator operator++(int) {
        RangeIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    bool operator==(const RangeIterator& rhs) const {
        return current == rhs.current;
    }
    bool operator!=(const RangeIterator& rhs) const {
        return !(*this == rhs);
    }
};

// Usage
RangeIterator it{0};
std::cout << *it++;   // prints 0, it is now 1
std::cout << *++it;   // prints 2, it is now 2
```

## Common Pitfalls

### 1. Returning `*this` from Postfix

```cpp
Counter& operator++(int) {  // WRONG
    ++value;
    return *this;            // returns the NEW value, not the old — breaks  x = c++
}
```

Post-increment must save the old state first.

### 2. Not Delegating Postfix to Prefix

Implementing the logic twice creates maintenance burden and risks divergence:

```cpp
// BAD — duplicated logic
Counter operator++(int) {
    Counter old = *this;
    value++;            // duplicated increment logic
    return old;
}
```

Always call `++(*this)` (or `operator++()`) from within postfix.

### 3. Confusing the Dummy Parameter

The `int` in `operator++(int)` is **never passed** — it is just a tag. You cannot name it or use it:

```cpp
Counter operator++(int /* unnamed, unused */) { ... }
```

## Quick Reference

| Form | Syntax | Signature | Returns |
|------|--------|-----------|---------|
| Prefix | `++x` | `T& operator++()` | `*this` by ref |
| Postfix | `x++` | `T operator++(int)` | old copy by value |

> **Interview answer:** Postfix increment takes a dummy `int` parameter to distinguish it from prefix. It saves the old value as a copy, calls the prefix form to mutate, and returns the old copy by value. Prefix is preferred in loops because postfix requires an extra copy.
