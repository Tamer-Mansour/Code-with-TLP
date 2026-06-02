# final, override, and Covariant Return Types

C++11 introduced two context-sensitive keywords — `override` and `final` — that close common correctness gaps in inheritance hierarchies. Covariant return types are an older rule that lets overrides return a more-derived pointer/reference type.

## `override`

`override` tells the compiler: "this function must override a virtual function in a base class." If the signature does not match any base virtual exactly, the program is **ill-formed** (compile error).

```cpp
struct Base {
    virtual void process(int x) const;
    virtual int  compute() const;
};

struct Derived : Base {
    void Process(int x) const override;   // ERROR: no 'Process' in Base
    void process(int x) override;         // ERROR: missing 'const'
    void process(int x) const override;   // OK
    long compute() const override;        // ERROR: return type mismatch (not covariant)
};
```

Without `override`, the first two would silently create **new** functions, breaking polymorphism. Always use it on every override.

## `final` on a Virtual Function

`final` on a member function means: "no further derived class may override this function." It also enables **devirtualization** — the compiler knows the final target and may optimize the virtual call into a direct call.

```cpp
struct Base {
    virtual void render() const;
};

struct Mid : Base {
    void render() const override final;  // cannot be overridden further
};

struct Leaf : Mid {
    void render() const override;  // ERROR: Mid::render is final
};
```

## `final` on a Class

Applied to a class, `final` prevents any class from inheriting from it. Every virtual call to objects of that class can be devirtualized by the compiler.

```cpp
struct Singleton final {
    static Singleton& instance();
    virtual void op();   // virtual allowed inside a final class (but dispatch is optimized)
};

struct SubSingleton : Singleton {};   // ERROR: cannot derive from final class
```

```cpp
void process(Singleton& s) {
    s.op();    // compiler knows s must be Singleton (no derived) → direct call
}
```

## Combining `override` and `final`

A function can be both — it overrides the base and prevents further overriding:

```cpp
struct Shape {
    virtual double area() const = 0;
};

struct Circle final : Shape {
    double area() const override final {   // overrides Shape, cannot be overridden
        return 3.14159 * r * r;
    }
    double r{1.0};
};
```

## Covariant Return Types

Normally an override must return the **exact same type** as the base virtual. The exception: if the base returns `Base*` (or `Base&`), the override may return `Derived*` (or `Derived&`) — a **covariant** return type. The relationship must be a public base.

```cpp
struct Node {
    virtual Node* clone() const {
        return new Node(*this);
    }
};

struct LeafNode : Node {
    LeafNode* clone() const override {   // covariant: LeafNode* is-a Node*
        return new LeafNode(*this);
    }
};

LeafNode* leaf = new LeafNode();
LeafNode* copy = leaf->clone();   // no cast needed — returns LeafNode*
```

Covariant return types are especially useful for the **Prototype pattern**: the base `clone()` returns a `Base*`, but callers with a concrete pointer get a concrete type back without a `static_cast`.

## Rules Summary

| Feature | Meaning | Benefit |
|---------|---------|---------|
| `override` | Must match a base virtual | Compile-time typo/signature protection |
| `final` (function) | No further override allowed | Devirtualization opportunity |
| `final` (class) | No further inheritance | Full devirtualization of all methods |
| Covariant return | Override may narrow return type | Cleaner API — avoids casts at call site |

## Key Pitfall: `override` Without `virtual`

`override` can only appear on a function that overrides a base `virtual`. Attempting it on a non-virtual function is an error:

```cpp
struct Plain {
    void run();         // not virtual
};

struct Sub : Plain {
    void run() override;   // ERROR: Plain::run is not virtual
};
```

**Interview answer:** `override` enforces that a function matches a base virtual (compile error if not); `final` prevents further overriding and enables compiler devirtualization; covariant return types allow an override to return a more-derived pointer or reference type, eliminating casts in clone/factory patterns.
