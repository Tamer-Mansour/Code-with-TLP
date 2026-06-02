# The Copy Assignment Operator

The copy assignment operator defines what happens when you assign one already-constructed object to another already-constructed object. It is distinct from the copy constructor: the copy constructor creates a new object, while copy assignment **replaces the state of an existing one**.

## Signature

```cpp
class MyClass {
public:
    MyClass& operator=(const MyClass& rhs);
};
```

The return type is `MyClass&` (a reference to `*this`) so that chained assignments work: `a = b = c`.

## The Fundamental Problem: Releasing Old Resources

Before copying data from `rhs`, you must **free whatever resource the object currently owns**. Forgetting this causes a memory leak.

```cpp
class Buffer {
    int* data_;
    int  size_;
public:
    Buffer& operator=(const Buffer& rhs) {
        // Step 1: release old resource
        delete[] data_;

        // Step 2: allocate new storage
        size_ = rhs.size_;
        data_ = new int[rhs.size_];

        // Step 3: copy the contents
        std::copy(rhs.data_, rhs.data_ + rhs.size_, data_);

        // Step 4: return self-reference
        return *this;
    }
};
```

This is the naive version. It has a critical flaw: **self-assignment** (`buf = buf`) deletes the data before trying to copy it. The self-assignment lesson covers the fix.

## Step-by-Step Breakdown

| Step | Action | Why |
|---|---|---|
| 1 | `delete[] data_` | Release the resource we currently own |
| 2 | Allocate new memory | Claim independent storage |
| 3 | Copy contents | Deep copy semantics |
| 4 | `return *this` | Enable chaining |

## Protecting Against Allocation Failure

If `new` throws, the object is left with a dangling `data_` pointer (already deleted in step 1). The strong exception-safety guarantee requires allocating first, then releasing:

```cpp
Buffer& operator=(const Buffer& rhs) {
    if (this == &rhs) return *this;     // self-assignment guard

    int* tmp = new int[rhs.size_];      // allocate first (may throw)
    std::copy(rhs.data_, rhs.data_ + rhs.size_, tmp);

    delete[] data_;                     // release old only after success
    data_ = tmp;
    size_ = rhs.size_;
    return *this;
}
```

Now if `new` throws, the old state is intact — the operation has no effect (strong guarantee).

## Difference From Copy Constructor

```cpp
Buffer a(10);    // constructor
Buffer b = a;    // copy constructor — b does not exist yet
b = a;           // copy assignment — b already holds data_
```

The compiler cannot distinguish `Buffer b = a` (copy-init, calls copy constructor) from `b = a` (assignment). The presence or absence of `= a` on the **declaration line** is the deciding factor.

## When the Compiler Generates It

The compiler generates a memberwise copy assignment operator unless you declare one yourself (or if the class contains a `const` member or reference member, in which case it is deleted). The generated version performs a **shallow** memberwise assignment — safe for value types, dangerous for owning raw pointers.

## Returning `*this`

Always return `MyClass&` and `return *this`. This mirrors the behaviour of built-in assignment and enables:

```cpp
a = b = c;        // right-associative: a = (b = c)
(a = b).display(); // assignment as a sub-expression
```

## Common Pitfalls

- **Missing self-assignment check** — leads to deleting then reading from freed memory.
- **Forgetting to release old data** — memory leak every time you assign to a non-empty object.
- **Not returning `*this`** — chained assignment gives a compiler error or garbage.
- **Declaring but not implementing** — if you declare `operator=` in the header but forget to define it, you get a linker error.

> **Interview answer:** The copy assignment operator must first release any resource the left-hand object owns, then deep-copy the right-hand side's data. It must return `*this`, guard against self-assignment, and — for strong exception safety — allocate new memory before freeing the old.
