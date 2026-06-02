# The this Pointer and Member Resolution

Every non-static member function receives a hidden first parameter: a pointer to the object on which the function was called. C++ names this pointer `this`. Understanding it demystifies how method calls work under the hood.

## What `this` Is

When you write:

```cpp
timer.start();
```

The compiler rewrites it roughly as:

```cpp
Timer::start(&timer);   // pseudocode — how the call is lowered
```

Inside `start`, the name `this` refers to `&timer` — a pointer of type `Timer*` (or `const Timer*` inside a `const` method).

```cpp
class Timer {
public:
    void start() {
        // 'this' here has type Timer*
        this->running_ = true;   // explicit — same as just: running_ = true
    }
private:
    bool running_ = false;
};
```

Writing `this->member` is always valid; it is simply verbose. The compiler inserts it implicitly when you write `member` alone inside a method.

## When You *Must* Use `this` Explicitly

### 1. Disambiguating shadowed names

```cpp
class Counter {
public:
    void setCount(int count) {
        this->count = count;   // 'count' parameter vs 'count' member
    }
private:
    int count = 0;
};
```

Without `this->`, both `count` on the right and left would refer to the parameter. The member would never be updated.

### 2. Returning the object itself (fluent / builder pattern)

```cpp
class QueryBuilder {
public:
    QueryBuilder& where(const char* condition) {
        // append condition …
        return *this;   // return reference to self for chaining
    }
    QueryBuilder& limit(int n) {
        limit_ = n;
        return *this;
    }
private:
    int limit_ = 100;
};

// Usage
QueryBuilder q;
q.where("age > 18").limit(50);  // method chaining
```

`*this` dereferences the pointer to give a reference to the current object.

### 3. Passing the current object to another function

```cpp
class Node {
public:
    void registerWith(Registry& reg) {
        reg.add(this);   // pass pointer to self
    }
};
```

## `this` and `const` Methods

In a `const` member function, `this` has type `const ClassName*`. You cannot modify data members through it (unless they are marked `mutable`).

```cpp
class Sensor {
public:
    int read() const {
        // this has type: const Sensor*
        // raw_value_ = 0;  // ERROR — const method cannot modify member
        return raw_value_;
    }
private:
    int raw_value_ = 0;
};
```

## `this` Is Never Null (For Valid Objects)

The C++ standard guarantees that `this` is never null for a correctly formed call. Code that dereferences a null pointer before calling a method is undefined behaviour *before* `this` is even used.

```cpp
Timer* t = nullptr;
t->start();   // UB — do not do this
```

## Under the Hood: ABI Perspective

On x86-64 (System V AMD64 ABI), `this` is passed in the `rdi` register — the same register used for the first explicit argument in a plain C function. The member function calling convention is therefore identical to a free function with an extra pointer argument, which is why C++ objects carry no per-object overhead for their methods.

```asm
; Timer::start() compiled (simplified)
; rdi = this (pointer to Timer object)
start:
    movb $1, 0(%rdi)    ; this->running_ = true
    ret
```

## Worked Example: Linked List Node Splice

```cpp
class ListNode {
public:
    int       value;
    ListNode* next = nullptr;

    // Insert 'other' after this node; return 'other' for chaining
    ListNode* insertAfter(ListNode* other) {
        other->next = this->next;
        this->next  = other;
        return other;   // caller can chain further insertions
    }
};

ListNode a{1}, b{2}, c{3};
a.insertAfter(&b)->insertAfter(&c);
// chain: a -> b -> c
```

---

> **Interview answer:** "`this` is a hidden pointer to the current object, implicitly passed to every non-static member function. It is used explicitly when a member name is shadowed by a parameter, when returning `*this` for method chaining, or when passing the object's address to another function. In `const` methods `this` is `const T*`, preventing mutation."
