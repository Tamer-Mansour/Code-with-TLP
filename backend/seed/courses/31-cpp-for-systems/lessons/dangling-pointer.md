# Dangling Pointers and Use-After-Free

## What Is a Dangling Pointer?

A dangling pointer is a pointer that holds the address of memory that has already been freed or gone out of scope. The pointer's bits still contain the old address, but that address no longer refers to valid, owned memory. Any access through it is **undefined behavior**.

```cpp
int* dangle() {
    int x = 42;
    return &x;   // x is destroyed when the function returns
}                // the returned pointer dangles immediately

int main() {
    int* p = dangle();
    *p = 100;    // UB: writing to a stack frame that no longer exists
}
```

## Use-After-Free on the Heap

The most dangerous variant occurs after `delete`:

```cpp
int* p = new int(10);
delete p;        // memory returned to the allocator

*p = 20;         // USE-AFTER-FREE — UB
std::cout << *p; // also UB: may read 20, garbage, or crash
```

Why is this so dangerous?

1. The allocator may have immediately reused the memory for another object.
2. Writing to it corrupts the other object silently.
3. Reading from it returns unpredictable data — which may look valid.
4. The crash, if any, often occurs far from the bad access, making debugging hard.

## Common Scenarios

### Storing a Pointer to a Deleted Object

```cpp
struct Node { int val; Node* next; };

Node* head = new Node{1, nullptr};
Node* alias = head;   // alias points to the same Node
delete head;
alias->val = 99;      // USE-AFTER-FREE — alias is now dangling
```

### Iterator / Reference Invalidation

```cpp
#include <vector>
std::vector<int> v = {1, 2, 3};
int* ref = &v[0];   // direct pointer into the vector's buffer
v.push_back(4);     // may reallocate! ref is now dangling
std::cout << *ref;  // UB
```

### Returning References to Locals

```cpp
std::string& get_name() {
    std::string name = "Alice";
    return name;   // WARNING: returning reference to local variable
}
// The returned reference dangles immediately
```

## The "Null After Delete" Pattern

A common defensive habit is to zero the pointer after deletion:

```cpp
delete p;
p = nullptr;

// Now accidental dereference crashes loudly instead of silently corrupting:
*p = 5;  // segfault — much easier to debug than silent corruption
```

This does **not** fix aliasing problems — other pointers to the same address remain dangling. But it makes the owning pointer self-diagnosing.

## Detecting Use-After-Free

### AddressSanitizer (ASan)

```bash
g++ -fsanitize=address -g uaf.cpp -o uaf
./uaf
```

```
ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010
READ of size 4 at 0x602000000010 thread T0
    #0 0x... in main uaf.cpp:8
previously freed by thread T0 here:
    #0 0x... in operator delete(void*) ...
    #1 0x... in main uaf.cpp:6
```

ASan poisons freed memory so any subsequent read or write is caught immediately.

### Valgrind

```bash
valgrind --tool=memcheck ./uaf
# ==...== Invalid read of size 4
# ==...==  Address 0x... is 0 bytes inside a block of size 4 free'd
```

## Worked Example: Safe Ownership Transfer

```cpp
#include <memory>

struct Resource {
    int id;
    explicit Resource(int i) : id(i) {}
};

int main() {
    auto owner = std::make_unique<Resource>(7);
    Resource* raw = owner.get();   // non-owning observer

    // When owner goes out of scope, raw becomes dangling.
    // unique_ptr makes ownership explicit and prevents double-delete.
    owner.reset();       // explicitly release

    // raw is now dangling — don't use it
    // raw->id would be UB
}
```

The fix: do not store raw pointers that outlive the owning smart pointer, or use `std::weak_ptr` with `std::shared_ptr` to detect invalidation safely.

## Interview Answer

> **Q: What is a use-after-free vulnerability and why is it dangerous in security contexts?**
>
> After memory is freed, an attacker can trigger a controlled re-allocation of that region with attacker-controlled data; when the program then uses its dangling pointer to the same region, it operates on the attacker's data — enabling type confusion, arbitrary code execution, or privilege escalation.
