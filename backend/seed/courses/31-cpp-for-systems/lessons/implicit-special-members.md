# Compiler-Generated Special Member Functions

C++ compilers automatically generate up to six special member functions when you do not declare them yourself. Knowing the exact rules for when each one is generated — and when it is suppressed or deleted — prevents subtle bugs and lets you write classes with confidence.

## The Six Special Member Functions

| Function | Syntax |
|---|---|
| Default constructor | `T()` |
| Destructor | `~T()` |
| Copy constructor | `T(const T&)` |
| Copy assignment operator | `T& operator=(const T&)` |
| Move constructor (C++11) | `T(T&&)` |
| Move assignment operator (C++11) | `T& operator=(T&&)` |

## Generation Rules (C++11)

### Default Constructor

Generated **only if no user-declared constructor exists at all**. The moment you write any constructor (even `explicit Foo(int)`), the default constructor is suppressed.

```cpp
struct A { int x; };      // default ctor generated
struct B { B(int x); };   // no default ctor — must use B(int)
```

### Destructor

Always generated unless you declare one. The generated destructor calls the destructors of all base classes and member variables in reverse construction order.

### Copy Constructor

Generated if the user has not declared a copy constructor **and** no move operation (move ctor or move assignment) has been declared.

```cpp
struct Good { std::string name; };  // copy ctor generated (memberwise)

struct HasMove {
    HasMove(HasMove&&) {}           // user-declared move ctor
    // copy ctor is now DELETED implicitly
};
```

### Copy Assignment Operator

Generated under the same conditions as the copy constructor. Additionally, it is **deleted** (not merely suppressed) if any member is `const` or a reference, because you cannot reassign those.

```cpp
struct Immutable {
    const int id;                   // copy assign deleted — can't reassign const
    Immutable(int i) : id(i) {}
};
```

### Move Constructor and Move Assignment (C++11)

Generated **only if**:
- No user-declared copy constructor
- No user-declared copy assignment operator
- No user-declared destructor
- No user-declared move operation of the other kind

This is the most restrictive rule: declaring **any** of the five other specials suppresses the generated move operations.

## What "Memberwise" Means

The compiler-generated copy constructor calls each member's own copy constructor:

```cpp
struct Inner { int x; };
struct Outer {
    Inner a;
    Inner b;
    // generated copy ctor is equivalent to:
    // Outer(const Outer& o) : a(o.a), b(o.b) {}
};
```

For **pointer members**, the memberwise copy copies the address — this is the shallow copy problem.

## The Interaction Matrix

| User declares | Default ctor | Copy ctor | Copy assign | Move ctor | Move assign |
|---|---|---|---|---|---|
| Nothing | Generated | Generated | Generated | Generated | Generated |
| Any constructor | **Not generated** | Generated | Generated | Generated | Generated |
| Destructor | Generated | Generated* | Generated* | **Not generated** | **Not generated** |
| Copy ctor | Generated | — (user) | Generated* | **Not generated** | **Not generated** |
| Move ctor | Generated | **Deleted** | **Deleted** | — (user) | Not generated |

*Generated but deprecated in some compilers when destructor is present (pending removal in future standard).

## `= default` and `= delete`

You can explicitly request or forbid generation:

```cpp
class Managed {
public:
    Managed() = default;                       // force generation
    Managed(const Managed&) = delete;          // forbid copying
    Managed& operator=(const Managed&) = delete;
    ~Managed() = default;
};
```

`= default` is useful when you have declared other constructors but still want the compiler to generate the default one, **or** to re-enable a copy constructor that would otherwise be deleted.

## Practical Guidance

- If your class only contains value-type members or `std::` containers, trust the generated specials.
- If your class contains a raw owning pointer, apply the Rule of Three (or Five) and write all required specials explicitly.
- If you want to suppress a special member for clarity or safety, prefer `= delete` over a private unimplemented declaration (the old C++03 trick).

> **Interview answer:** The compiler generates the default constructor, copy constructor, copy assignment operator, destructor, move constructor, and move assignment operator under specific conditions. Most importantly, declaring any move operation deletes the generated copy operations, and declaring a destructor suppresses the generated move operations — so a class with a user-defined destructor and raw pointer needs explicit copy members to avoid shallow-copy bugs.
