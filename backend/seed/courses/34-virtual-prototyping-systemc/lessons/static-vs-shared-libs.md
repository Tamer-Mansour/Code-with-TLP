# Static vs Shared Libraries

When you build a SystemC simulator, you must link it against the SystemC runtime library. You have two choices: a **static library** (`.a` on Linux, `.lib` on Windows) or a **shared library** (`.so` on Linux, `.dll` on Windows). The choice affects binary size, startup time, deployment, and versioning.

## What Is a Library?

A library is a collection of compiled object files bundled together so other programs can use their code. The bundling format is the only difference between static and shared.

## Static Libraries

A static library is an archive of `.o` files created with `ar`:

```bash
ar rcs libmyip.a block1.o block2.o block3.o
```

At **link time**, the linker copies only the object files it actually needs from the archive into the final executable. The result is a **self-contained binary** — no external runtime dependency.

```bash
g++ main.o -L./lib -lmyip -lsystemc -o sim_static
```

| Pros | Cons |
|------|------|
| No runtime dependency | Larger executable |
| Faster startup (no dynamic loading) | Multiple executables duplicate code in memory |
| Simpler deployment | Recompile all binaries to update the library |

## Shared Libraries

A shared library is a compiled, position-independent `.so` or `.dll` that is loaded by the OS loader at process startup (or on demand with `dlopen`).

```bash
# Build a shared library
g++ -fPIC -shared block1.cpp block2.cpp -o libmyip.so

# Link an executable against it
g++ main.o -L. -lmyip -o sim_shared
```

The `-fPIC` flag generates **Position-Independent Code**, required because the library will be mapped to an arbitrary virtual address in each process.

| Pros | Cons |
|------|------|
| Shared in memory across processes | Must be present at runtime |
| Update library without relinking apps | Slower first load (symbol resolution) |
| Plugin architectures possible | "DLL hell" / version conflicts |

## SystemC Library Variants

The SystemC reference implementation ships as both:

- `libsystemc.a` — static, commonly used for final simulation executables
- `libsystemc.so` — shared, useful when multiple simulators run simultaneously

```bash
# Using the static library (most common in VP projects)
g++ -c top.cpp -I/opt/systemc/include
g++ top.o -L/opt/systemc/lib -lsystemc -lpthread -o sim
```

```bash
# Runtime path for shared library
export LD_LIBRARY_PATH=/opt/systemc/lib:$LD_LIBRARY_PATH
./sim
```

## Position-Independent Code

Any code linked into a shared library must be compiled with `-fPIC`. Failing to do so causes a linker error like:

```
relocation R_X86_64_32 against `.rodata' can not be used when making a shared object
```

## Checking What a Binary Needs

```bash
ldd ./sim             # list shared library dependencies
nm -u ./sim           # list undefined symbols (will be resolved at load time)
file ./sim            # statically or dynamically linked?
```

## Symbol Visibility

By default, all symbols in a shared library are exported. Use visibility attributes to reduce the public surface and speed up linking:

```cpp
__attribute__((visibility("default"))) void public_api();   // exported
__attribute__((visibility("hidden")))  void internal_impl(); // not exported
```

Or compile with `-fvisibility=hidden` and mark only public symbols explicitly.

## Worked Example — Choosing for a VP Project

A virtual platform that runs on a CI server alongside 20 other simulators benefits from shared SystemC so the OS can share one copy of the runtime in physical memory. A standalone deliverable distributed to a customer with no SystemC installed must use the static library.

## Interview Answer

> "A static library is copied into the executable at link time — no runtime dependency, larger binary. A shared library is loaded at runtime — smaller binary, shared memory, but the `.so` must be present and on `LD_LIBRARY_PATH`."
