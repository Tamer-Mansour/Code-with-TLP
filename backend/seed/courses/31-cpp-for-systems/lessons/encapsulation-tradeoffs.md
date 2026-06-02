# Encapsulation Tradeoffs in Performance-Critical Code

Encapsulation is not free. Every indirection — a virtual call, a getter function, a Pimpl dereference — has a cost. In performance-critical systems code (real-time DSP, packet processing, game engines, OS hot paths) you must weigh the maintenance value of encapsulation against measurable runtime overhead. This lesson maps the tradeoffs so you can make deliberate choices.

## The Overhead Sources

| Mechanism | Cost | When it matters |
|---|---|---|
| Virtual dispatch | ~2-5 ns per call (icache miss on cold code) | Hot loops, millions of calls/sec |
| Pimpl indirection | One extra pointer dereference | Cache-sensitive tight loops |
| Inline getter | Zero (inlined by compiler) | Never a problem |
| `std::function` wrapper | ~10-20 ns (possible heap alloc) | High-frequency callbacks |
| `private` + setter validation | Branch prediction cost | Extremely tight inner loops |

## Inlining as the Reconciler

Most accessor overhead disappears when the compiler inlines the call. Mark small getters `inline` (or define them in the header) and enable optimisation (`-O2` / `/O2`):

```cpp
class Vec3 {
public:
    float x() const { return x_; }  // defined in header → always inlinable
    float y() const { return y_; }
    float z() const { return z_; }
private:
    float x_, y_, z_;
};
```

After inlining, `v.x()` compiles to a single `mov` — identical to `v.x_` direct access. **Measure before sacrificing encapsulation**.

## Virtual Dispatch in Hot Loops

Virtual calls prevent inlining and can cause branch mispredicts on cold code paths:

```cpp
// Virtual: indirection through vtable, cannot be inlined
for (auto& shape : shapes)
    total_area += shape->area();  // indirect call

// Non-virtual with known types: direct call, fully inlinable
for (auto& circle : circles)
    total_area += circle.area();  // direct, fast
```

Techniques to keep encapsulation without paying virtual overhead:

- **CRTP (Curiously Recurring Template Pattern)**: compile-time polymorphism, zero virtual overhead.
- **`std::variant` + `std::visit`**: closed-set polymorphism without vtable.
- **Devirtualisation**: some compilers devirtualise when the concrete type is visible at the call site.

```cpp
// CRTP: polymorphism with zero runtime cost
template<typename Derived>
class Shape {
public:
    float area() const { return static_cast<const Derived*>(this)->area_impl(); }
};

class Circle : public Shape<Circle> {
    float area_impl() const { return 3.14159f * r_ * r_; }
    float r_;
};
```

## Data Layout vs. Encapsulation

Encapsulation may scatter data across multiple objects. In a particle system, iterating one field across 100,000 objects benefits from struct-of-arrays (SoA) layout:

```cpp
// AoS (Array of Structs) — encapsulation-friendly, cache-unfriendly
struct Particle { float x, y, z, vx, vy, vz; float mass; };
std::vector<Particle> particles;

// SoA (Struct of Arrays) — cache-friendly, harder to encapsulate
struct ParticleSystem {
    std::vector<float> x, y, z;    // positions
    std::vector<float> vx, vy, vz; // velocities
    std::vector<float> mass;
};
```

SoA is faster for SIMD because a single cache line carries 16 floats of the same field. The tradeoff: `ParticleSystem` is awkward to encapsulate because "a single particle" has no natural object boundary. Many high-performance engines expose a hybrid API that presents encapsulated particle handles while storing data in SoA internally.

## When to Relax Encapsulation

- **Profile-guided decisions only** — measure with a profiler (`perf`, VTune, Tracy); do not guess.
- **Inner-loop structs** — plain `struct` with `public` fields is idiomatic for POD hot-path data.
- **POD network packets, hardware descriptors** — these are memory-mapped or wire-format; layout must match exactly, making getters misleading.
- **`friend` in unit tests** — acceptable to expose internals to the test binary only.

## Retaining Encapsulation at the Right Granularity

The encapsulation unit does not have to be the class — it can be the **module** or **subsystem**:

```cpp
// Internal to physics.cpp — raw struct, no ceremony
struct RigidBody { float x, y, z, mass; uint32_t flags; };

// External API — fully encapsulated, physics internals hidden
class PhysicsWorld {
public:
    RigidBodyHandle add_body(float x, float y, float z, float mass);
    void            step(float dt);
    Vec3            get_position(RigidBodyHandle h) const;
};
```

`RigidBody` is `struct` for performance; `PhysicsWorld` is a class for API stability. The hot inner loop manipulates raw structs; callers never see them.

## Interview Answer

> "Encapsulation overhead is mostly inlining noise — measure first. Virtual dispatch in hot loops has a real cost; CRTP or std::variant provides polymorphism without it. For cache-critical data layouts, keep encapsulation at the subsystem boundary rather than the per-object level."
