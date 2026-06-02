# friend Functions and Classes

The `friend` keyword grants a specific external function or class full access to another class's `private` and `protected` members. It is a controlled, named exception to encapsulation — not a loophole, but a deliberate design choice.

## `friend` Functions

A free (non-member) function declared as `friend` inside a class may read and write that class's private members:

```cpp
class Vector2 {
public:
    Vector2(double x, double y) : x_(x), y_(y) {}

    // Grant the free operator access to private fields
    friend Vector2 operator+(const Vector2& a, const Vector2& b);

private:
    double x_, y_;
};

Vector2 operator+(const Vector2& a, const Vector2& b) {
    return Vector2(a.x_ + b.x_, a.y_ + b.y_);  // direct access to x_, y_
}

// Usage
Vector2 v1(1.0, 2.0), v2(3.0, 4.0);
Vector2 v3 = v1 + v2;   // calls operator+
```

The `friend` declaration *inside* the class grants access; the function *definition* lives outside.

## `friend` Classes

An entire class can be declared a friend, granting all of its methods access to the befriended class's private members:

```cpp
class Engine;   // forward declaration

class Car {
    friend class Engine;   // Engine can read/write all of Car's privates
private:
    int horsepower_ = 0;
    int rpm_        = 0;
};

class Engine {
public:
    void tune(Car& c) {
        c.horsepower_ = 400;   // OK — Engine is a friend of Car
        c.rpm_        = 6000;
    }
};
```

Friendship is **one-directional**: `Car` granting friendship to `Engine` does not give `Car` access to `Engine`'s privates.

## When to Use `friend`

Good use cases:

- **Overloaded operators** (`<<`, `>>`, `+`, `-`, `==`) that need access to private data but cannot be members because the left operand is not of the class type.
- **Unit test classes** — a test fixture that needs to inspect private state.
- **Tightly coupled pairs** — e.g., an iterator class that must walk a container's internal nodes.

```cpp
class LinkedList {
    friend class Iterator;   // Iterator navigates private nodes
private:
    struct Node { int val; Node* next; };
    Node* head_ = nullptr;
};
```

## `friend` and `operator<<`

The most common `friend` function in C++ is the stream-insertion operator:

```cpp
class Packet {
public:
    Packet(uint32_t id, uint16_t len) : id_(id), len_(len) {}

    friend std::ostream& operator<<(std::ostream& os, const Packet& p) {
        return os << "Packet{id=" << p.id_ << ", len=" << p.len_ << '}';
    }

private:
    uint32_t id_;
    uint16_t len_;
};

Packet pkt(42, 1500);
std::cout << pkt << '\n';   // Packet{id=42, len=1500}
```

The left operand is `std::ostream&`, not `Packet`, so the operator cannot be a member of `Packet`. A `friend` free function is the standard solution.

## Key Properties

- Friendship is **not inherited**: a class derived from `Car` does not inherit friendship with `Engine`.
- Friendship is **not transitive**: if `A` is a friend of `B` and `B` is a friend of `C`, `A` is not a friend of `C`.
- The `friend` declaration may appear in any access section (`public`, `private`, `protected`) — it has the same effect regardless.

## Common Pitfalls

- **Friendship instead of a better API** — if you find yourself making many things friends of a class, the class probably needs a richer public interface instead.
- **`friend` for test access** — acceptable, but consider whether a `protected` inner class or a dedicated accessor is cleaner.
- **Assuming mutual friendship** — granting friendship in one direction does not open the reverse channel.

---

> **Interview answer:** "The `friend` keyword grants a specific function or class full access to another class's private and protected members. It is used for overloaded operators that cannot be members (like `operator<<`), for tightly coupled iterator–container pairs, and for test fixtures. Friendship is non-inherited and non-transitive."
