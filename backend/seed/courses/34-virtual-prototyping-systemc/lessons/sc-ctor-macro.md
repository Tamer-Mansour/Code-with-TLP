# SC_CTOR and Module Constructors

Every SystemC module must have a constructor that registers itself with the simulation kernel and declares its internal processes. `SC_CTOR` is the standard macro for writing that constructor concisely and correctly.

## What SC_CTOR Expands To

```cpp
SC_CTOR(MyModule) {
    // body
}
```

expands to:

```cpp
MyModule(sc_module_name name_) : sc_module(name_) {
    // body
}
```

The `sc_module_name` parameter is a thin wrapper around a `const char*`. The base class `sc_module` uses it to register the instance in the hierarchical name tree. Without passing it to `sc_module(name_)`, the module would be unnamed and the kernel could not build the object hierarchy.

## Why sc_module_name and Not const char*

`sc_module_name` is a *guard object*. The SystemC kernel uses a thread-local stack of pending names. When you write:

```cpp
MyModule inst("my_inst");
```

the string `"my_inst"` is pushed onto the kernel's internal name stack *before* the constructor runs. `sc_module_name` in the constructor parameter list pops it. This scheme ensures that every `sc_module` receives the name of the enclosing context without manual bookkeeping.

## Registering Processes in the Constructor

The constructor body is the only legal place to register processes. Three macros are available:

| Macro | Trigger | Typical Use |
|---|---|---|
| `SC_METHOD(func)` | Re-runs on any sensitive event; no state between calls | Combinational logic |
| `SC_THREAD(func)` | Runs once, can call `wait()` | Behavioral / bus-functional |
| `SC_CTHREAD(func, clk.pos())` | Clocked thread | RTL-style sequential logic |

After declaring a process you set its sensitivity list:

```cpp
SC_CTOR(Adder) {
    SC_METHOD(compute);
    sensitive << a << b;   // re-evaluate whenever a or b changes
}
```

`sensitive` is a member of `sc_module` and returns a reference to the current process's sensitivity list. Chaining `<<` adds each signal or port to that list.

## Member Initializer Lists

Because `SC_CTOR` expands to a normal constructor, you can (and should) initialize member variables and child modules using initializer lists:

```cpp
SC_MODULE(Pipeline) {
    sc_in<bool>   clk;
    sc_signal<int> pipe_sig;
    Stage1 s1;
    Stage2 s2;

    SC_CTOR(Pipeline)
        : s1("s1"),   // child module constructed with name
          s2("s2")
    {
        // port binding
        s1.clk(clk);
        s1.out(pipe_sig);
        s2.clk(clk);
        s2.in(pipe_sig);
    }
};
```

Initializing child modules in the initializer list is the idiomatic and safe approach because it guarantees construction order and avoids default-construction followed by assignment.

## When SC_CTOR Is Not Enough

`SC_CTOR` only supports one constructor signature. If you need to pass custom parameters (e.g., a configurable bit-width), write an explicit constructor instead:

```cpp
SC_MODULE(FifoBuffer) {
    int depth;
    // ...
    FifoBuffer(sc_module_name name_, int depth_)
        : sc_module(name_), depth(depth_)
    {
        SC_THREAD(run);
    }
};
```

This is the standard pattern for parameterized modules. Template modules (`SC_MODULE` + `template<typename T>`) follow the same rule.

## Common Pitfalls

- **Calling `wait()` inside the constructor.** The simulation has not started; the kernel will throw an error.
- **Registering the same process twice.** Each `SC_METHOD` / `SC_THREAD` call creates a new process handle; duplicate registrations create duplicate processes.
- **Setting sensitivity before declaring the process.** `sensitive` operates on the *last declared* process, so declaration must come first.
- **Using `SC_CTOR` with a parameterized module.** The macro does not accept extra arguments; write the constructor explicitly.

## Interview Answer

> **Interview answer:** `SC_CTOR(MyModule)` expands to a constructor taking `sc_module_name` and passes it to the `sc_module` base, registering the instance in the kernel hierarchy. The body is the only valid place to use `SC_METHOD`, `SC_THREAD`, and `sensitive` to declare and wire up processes before simulation starts.
