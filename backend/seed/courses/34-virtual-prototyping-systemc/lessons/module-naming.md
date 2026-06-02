# Module Names and the Object Hierarchy

Every module instance in a SystemC design lives in a tree called the *object hierarchy*. Understanding how names are assigned, how the tree is built, and how to query it is essential for debugging and for tools that traverse the design (waveform dumpers, coverage analyzers, TLM probes).

## How Names Are Assigned

When you write:

```cpp
Cpu cpu("cpu");
```

the string `"cpu"` is the *local name* of this instance. The SystemC kernel concatenates local names along the path from the top-level module down to this instance, separated by dots, to form the *hierarchical name*:

```
top.cpu
top.cpu.alu
top.cpu.alu.adder
```

This mirrors how hierarchical names work in VHDL and Verilog, and how EDA tools identify signals in simulation dumps (`.vcd`, `.fsdb`).

## sc_object and the Name API

`sc_module` inherits from `sc_object`, which provides:

```cpp
const char* name()       const;  // full hierarchical name, e.g. "top.cpu.alu"
const char* basename()   const;  // local name only, e.g. "alu"
const char* kind()       const;  // type string, e.g. "sc_module"
```

You can call `name()` anywhere after elaboration has started (i.e., inside a process or callback) to get the instance's place in the hierarchy.

## Retrieving the Object Tree at Runtime

The kernel provides a global accessor:

```cpp
sc_core::sc_get_top_level_objects(); // returns sc_pvector<sc_object*>
```

Each `sc_object*` in the list has a `get_child_objects()` method, allowing you to walk the entire tree recursively:

```cpp
void print_hierarchy(sc_object* obj, int depth = 0) {
    for (int i = 0; i < depth; ++i) std::cout << "  ";
    std::cout << obj->name() << " [" << obj->kind() << "]\n";
    for (auto* child : obj->get_child_objects())
        print_hierarchy(child, depth + 1);
}
```

This is how waveform dumpers discover which signals to record.

## Automatic vs. Manual Naming

When you use `SC_CTOR`, you always supply the name at the instantiation site:

```cpp
Cpu cpu("cpu");      // explicit, good
Cpu cpu2(cpu);       // copy — almost never correct
```

Never reuse the same name string for two instances at the same level. The kernel will warn or produce confusing diagnostics because both instances share the same hierarchical name.

For arrays of modules, generate names programmatically:

```cpp
for (int i = 0; i < 4; ++i) {
    char buf[16];
    std::snprintf(buf, sizeof(buf), "core_%d", i);
    cores[i] = new Core(buf);
}
// Results in: top.core_0, top.core_1, top.core_2, top.core_3
```

## The sc_module_name Guard

As discussed in the constructor lesson, `sc_module_name` is not merely a `const char*` alias. It is a RAII guard that interacts with a kernel-internal name stack. This stack exists to support automatic naming tools and legacy APIs. In modern SystemC code you always pass the name explicitly and should not rely on the implicit stack mechanism.

## Names in sc_trace (VCD Dumps)

When you call:

```cpp
sc_trace(tf, cpu.pc, "cpu.pc");
```

the third argument is the signal name as it will appear in the VCD file. Best practice is to use the signal's hierarchical name, which you can retrieve with:

```cpp
sc_trace(tf, cpu.pc, cpu.pc.name());
```

This keeps the VCD consistent with the design hierarchy and avoids manual typos.

## Common Pitfalls

- **Duplicate names at the same level.** Two children named `"bus"` under the same parent will produce confusing waveform signals and kernel warnings.
- **Using a temporary `char*` for the name.** The `sc_module_name` object copies the string, so stack temporaries are safe, but the name must be valid during construction.
- **Querying `name()` before elaboration.** During static C++ initialization (before `sc_main` runs), the hierarchy has not been built; `name()` may return garbage.

> **Interview answer:** Every `sc_module` instance receives a local name at construction time. The kernel concatenates parent and child local names with dots to form the hierarchical name (e.g., `top.cpu.alu`). The `name()` method on any `sc_object` returns this full path, which tools use to identify signals in waveform dumps and coverage databases.
