# Getters, Setters, and Class Invariants

A **class invariant** is a condition that must be true for every observable state of an object. Getters and setters are the gatekeepers that keep invariants intact. Used blindly they add noise; used intentionally they are a crucial correctness tool.

## What Is a Class Invariant?

Think of an invariant as a promise the class makes about itself at all times (before and after every public method call, and after construction).

Examples:

| Class | Invariant |
|---|---|
| `std::vector` | `size() <= capacity()` |
| `BoundedQueue<T, N>` | `0 <= count_ <= N` |
| `IpAddress` | Each octet in `[0, 255]` |
| `Mutex` | Either unlocked or owned by exactly one thread |

## Getters

A getter returns a view of private state. Key rules:

- Mark it `const` — a read should not modify the object.
- Return by value for scalars; return `const T&` for large objects when lifetime is clear.
- **Do not** return a non-const reference: `int& get_x()` is encapsulation suicide.

```cpp
class Circle {
public:
    double radius() const { return radius_; }   // good: const, by value
    // double& radius() { return radius_; }     // BAD: bypasses invariant
private:
    double radius_;
};
```

## Setters and Invariant Enforcement

A setter is the right place to **validate and reject** bad values:

```cpp
class Circle {
public:
    bool set_radius(double r) {
        if (r < 0.0) return false;   // invariant: radius >= 0
        radius_ = r;
        return true;
    }
private:
    double radius_ = 1.0;
};
```

Returning `bool` (or `std::expected`/`std::optional` in modern code) lets callers handle errors without exceptions — important in systems and embedded contexts where exceptions are often disabled.

## Constructor Invariants

The constructor must establish the invariant from scratch. If it cannot, it should throw (or, in no-exception environments, the class should expose a factory that returns an `Optional`).

```cpp
class RingBuffer {
public:
    explicit RingBuffer(size_t cap) : buf_(cap), cap_(cap) {
        if (cap == 0) throw std::invalid_argument("capacity must be > 0");
        // invariant: cap_ > 0 AND head_ < cap_ AND size_ <= cap_
    }
    // ...
private:
    std::vector<uint8_t> buf_;
    size_t cap_, head_ = 0, size_ = 0;
};
```

## Avoiding Getter/Setter Proliferation

A class with a public getter and setter for every private field is effectively a struct with extra ceremony. Ask:

- **Does the caller need raw access?** If yes, make the field public and use a `struct`.
- **Does the operation make more sense as a domain verb?** Prefer `account.deposit(50)` over `account.set_balance(account.balance() + 50)`.

```cpp
// Smell: tell-don't-ask violation
double b = account.balance();
account.set_balance(b + 50);

// Better: push the knowledge into the class
account.deposit(50);
```

## Checking Invariants in Debug Builds

Use `assert` (or a custom `DCHECK`) to verify invariants in debug builds without paying the cost in release:

```cpp
void RingBuffer::push(uint8_t byte) {
    assert(size_ < cap_ && "push on full buffer");
    buf_[(head_ + size_) % cap_] = byte;
    ++size_;
}
```

## Worked Example: Bounded Integer

```cpp
template<int Min, int Max>
class BoundedInt {
public:
    explicit BoundedInt(int v) {
        if (v < Min || v > Max)
            throw std::out_of_range("value out of bounds");
        val_ = v;
    }

    bool set(int v) {
        if (v < Min || v > Max) return false;
        val_ = v;
        return true;
    }

    int get() const { return val_; }

private:
    int val_;
    // Invariant: Min <= val_ <= Max always
};

BoundedInt<0, 100> percentage(50);
percentage.set(101); // returns false, val_ unchanged
```

## Interview Answer

> "A class invariant is a property that must hold for all valid objects. Setters enforce it by validating before updating; constructors establish it from scratch. Getters expose state safely by returning const views. The goal is that no sequence of public method calls can leave the object in an invalid state."
