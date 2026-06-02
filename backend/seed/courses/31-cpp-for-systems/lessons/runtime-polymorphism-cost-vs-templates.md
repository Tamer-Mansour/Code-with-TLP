# Runtime Polymorphism vs Templates: Tradeoffs

C++ gives you two mechanisms for writing generic, reusable code: **runtime polymorphism** (virtual functions / inheritance) and **compile-time polymorphism** (templates / concepts). Choosing the wrong one for a given situation is a common source of performance bugs or over-engineered designs.

## Side-by-Side Comparison

| Property | Runtime Polymorphism (virtuals) | Compile-Time Polymorphism (templates) |
|----------|---------------------------------|---------------------------------------|
| Type resolution | At runtime via vtable | At compile time |
| Binary size | One copy of each virtual function | One instantiation per concrete type |
| Inlining | Rarely (indirect call) | Frequently (direct call, fully visible) |
| Overhead per call | ~1 indirect branch + possible cache miss | Zero (inlined away) |
| Heterogeneous containers | `vector<Base*>` works naturally | Requires `std::variant` or type erasure |
| New types at runtime | Yes (shared libraries, plugins) | No — types must be known at compile time |
| Error messages | Linker / runtime errors | Often cryptic template errors |
| Compile time | Fast | Slow (heavy template instantiation) |

## The Virtual Function Overhead

A virtual call compiles to roughly:

```asm
mov  rax, [rdi]          ; load vtable pointer from object
call [rax + offset]      ; indirect call through vtable
```

Costs:
- One extra memory load (vtable pointer).
- The branch target is not known until runtime, so the branch predictor may mis-predict.
- The callee cannot be inlined into the caller.

On modern CPUs, this is **1–5 ns** per call — negligible for I/O-bound code, significant in tight inner loops (millions of calls per second).

## Template Approach: Static Duck Typing

```cpp
template<typename Logger>
void process(Logger& log) {
    log.write("start");       // resolved at compile time — can be inlined
    // ...
    log.write("end");
}

struct ConsoleLogger { void write(const char* s) { puts(s); } };
struct NullLogger    { void write(const char*  ) {}           };

ConsoleLogger cl;
process(cl);   // compiler generates process<ConsoleLogger> — fully inlined

NullLogger nl;
process(nl);   // compiler generates process<NullLogger> — zero overhead
```

No vtable, no indirection, and `NullLogger::write` is completely optimized away.

## When to Choose Runtime Polymorphism

- **Plugin or driver loading at runtime.** The concrete type is not known when the binary is compiled.
- **Heterogeneous collections.** A `vector<IWidget*>` can hold any widget subtype.
- **ABI stability.** A stable virtual interface lets you ship new concrete classes in a shared library without recompiling callers.
- **Call frequency is low.** I/O, RPC, GUI events — the virtual overhead is lost in the noise.

## When to Choose Templates

- **Performance-critical inner loops.** Sorting comparators, allocators, hash functions.
- **All types known at compile time.** Embedded firmware, statically linked systems.
- **Zero-overhead abstraction.** A templated `Ring<T, N>` lock-free buffer has no virtual overhead.
- **Policy-based design.** Compose behaviour at compile time without inheritance hierarchies.

## Mixing Both: Type Erasure

Sometimes you want the flexibility of runtime polymorphism with the zero-overhead potential of templates. Type erasure (used by `std::function`, `std::any`) bridges the gap:

```cpp
// std::function erases the concrete callable type at runtime
std::function<int(int)> f = [](int x){ return x * 2; };
```

For custom high-performance type erasure in systems code, hand-rolled vtable structs (sometimes called "fat pointers") are common.

## Concrete Recommendation for Systems Code

```
Call frequency     |  All types known  |  Runtime types?
                   |  at compile time  |
-------------------+-------------------+----------------
< 1 M calls/sec    |  Either fine      |  Virtual
1–100 M calls/sec  |  Template         |  Profile first
> 100 M calls/sec  |  Template ONLY    |  Avoid virtual
```

> **Interview answer:** Virtual functions resolve calls through a vtable at runtime (enabling runtime polymorphism and ABI stability but preventing inlining), while templates resolve at compile time (enabling zero-overhead inlining but requiring all types to be known at compile time and generating code per instantiation) — choose virtuals for plugins and heterogeneous containers, and templates for hot inner loops where all types are known.
