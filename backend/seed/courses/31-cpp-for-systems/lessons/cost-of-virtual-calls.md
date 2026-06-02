# The Cost of Virtual Calls and Devirtualization

Virtual dispatch is not free. In latency-sensitive systems code — game loops, audio engines, OS kernels, real-time control — the overhead of virtual calls can matter. Knowing exactly what you pay, and when the compiler can eliminate the cost, is essential.

## The Three Costs of a Virtual Call

### 1. Indirect call overhead

A direct call compiles to a single `call <fixed-address>` instruction. A virtual call compiles to:

```asm
mov  rax, [rdi]          ; load vptr   (1 memory read)
mov  rax, [rax + offset] ; load fptr   (1 memory read)
call rax                 ; indirect call
```

The CPU's branch predictor must predict an indirect branch target. A misprediction costs 10–20 cycles on modern microarchitectures.

### 2. Inhibits inlining

The compiler cannot inline a function it cannot see at the call site. Because the callee is not known until runtime, virtual calls effectively block inlining and all downstream optimizations (constant propagation, dead code elimination, loop unrolling).

### 3. Cache pressure

The vptr fetch brings the vtable into the data cache. If many different derived types are interleaved in a hot loop (cache-unfriendly object layout), each call may suffer a cache miss on the vptr or vtable itself.

## Micro-benchmark Perspective

A rough rule of thumb on modern x86-64 hardware:

| Call type | Approximate latency |
|-----------|---------------------|
| Direct call (non-inlined) | ~1–2 ns |
| Virtual call (hot cache) | ~3–5 ns |
| Virtual call (cold vptr) | ~15–50 ns |

These numbers are highly workload-dependent; always profile before optimizing.

## Devirtualization: Free Optimization

**Devirtualization** is the compiler transformation that turns a virtual call into a direct (or inlined) call when it can prove the dynamic type at compile time.

```cpp
void example() {
    Circle c(5.0);
    Shape& s = c;
    s.area();        // compiler sees the actual type is Circle
                     // → devirtualized to a direct call or even inlined
}
```

Devirtualization triggers when:
- The object is a local variable with a known concrete type.
- The function is declared `final` or the class is declared `final`.
- Whole-program optimization (LTO/PGO) proves the type across translation units.

```cpp
struct Circle final : Shape {  // 'final' enables devirtualization at call sites
    double area() const override { return 3.14159 * r * r; }
};
```

Check with Compiler Explorer (`godbolt.org`) — with `-O2` GCC/Clang often devirtualize obvious cases automatically.

## Techniques to Reduce Virtual Dispatch Overhead

### Batch by type (data-oriented design)

Instead of a heterogeneous array of base pointers, keep separate arrays per concrete type:

```cpp
// Slow: mixed types, vtable miss per element
std::vector<Shape*> shapes;

// Fast: process each type in a hot, type-homogeneous loop
std::vector<Circle> circles;
std::vector<Square> squares;
for (auto& c : circles) c.area();
for (auto& s : squares) s.area();
```

### std::variant + std::visit (zero-cost dispatch)

For a closed, known set of types, `std::variant` achieves type-safe polymorphism with no vtable:

```cpp
using AnyShape = std::variant<Circle, Square, Triangle>;

AnyShape shape = Circle{5.0};
double a = std::visit([](const auto& s) { return s.area(); }, shape);
```

`std::visit` compiles to a jump table indexed by the variant's type tag — no virtual overhead, inlinable.

### CRTP (Curiously Recurring Template Pattern)

Static polymorphism via templates:

```cpp
template<typename Derived>
struct Shape {
    double area() const {
        return static_cast<const Derived*>(this)->area_impl();
    }
};

struct Circle : Shape<Circle> {
    double area_impl() const { return 3.14159 * r * r; }
};
```

Zero runtime overhead; works only when all types are known at compile time.

## When Virtual Calls Are Fine

- Infrequent calls (UI events, I/O operations, system calls).
- Plugin/extension architectures where types are loaded at runtime.
- Any path that is not in a measured hot loop.

**Interview answer:** Virtual calls cost an indirect branch (vptr load + vtable index) and block inlining; the compiler can eliminate the cost via devirtualization when it can prove the concrete type — otherwise, prefer `std::variant`, CRTP, or type-sorted batching for hot paths.
