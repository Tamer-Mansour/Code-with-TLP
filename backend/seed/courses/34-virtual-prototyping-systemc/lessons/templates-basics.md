# Templates: Generic Modeling

Every SystemC port you have ever written — `sc_in<int>`, `sc_out<sc_uint<8>>`, `sc_signal<bool>` — is a **template instantiation**. Templates are C++'s mechanism for writing code once and reusing it with any type. For hardware modeling this is indispensable: a FIFO, an arbiter, or a bus matrix should not be rewritten for every data width.

## Function Templates

A function template lets you write a single function that works on multiple types.

```cpp
template<typename T>
T maximum(T a, T b) {
    return (a > b) ? a : b;
}

int    i = maximum(3, 7);       // T deduced as int
double d = maximum(2.5, 1.1);   // T deduced as double
```

The compiler generates a **separate concrete function** for each distinct type it encounters. There is no runtime overhead from the template mechanism itself.

## Class Templates

Class templates follow the same idea but for entire classes.

```cpp
template<typename T, int DEPTH>
class Fifo {
    T     buffer[DEPTH];
    int   head = 0, tail = 0, count = 0;
public:
    bool push(const T& item) {
        if (count == DEPTH) return false;
        buffer[tail++ % DEPTH] = item;
        count++;
        return true;
    }
    bool pop(T& item) {
        if (count == 0) return false;
        item = buffer[head++ % DEPTH];
        count--;
        return true;
    }
};

Fifo<int, 16>       intFifo;    // 16-slot int FIFO
Fifo<uint8_t, 256>  byteFifo;   // 256-slot byte FIFO
```

The non-type parameter `int DEPTH` allows compile-time constants to configure the size — exactly how `sc_uint<N>` encodes bit-width.

## How SystemC Uses Templates

| Template | Role |
|----------|------|
| `sc_signal<T>` | Generic signal carrying any copyable type |
| `sc_in<T>`, `sc_out<T>`, `sc_inout<T>` | Typed ports; bind-type mismatch is a compile error |
| `sc_fifo<T>` | Synthesisable FIFO channel |
| `tlm_initiator_socket<BUSWIDTH>` | TLM 2.0 socket parameterised by bus width |

Because the type is checked at compile time, connecting a `sc_in<int>` to an `sc_out<double>` is caught before the simulator ever runs.

## Template Specialisation

Sometimes a generic implementation doesn't work for a specific type. **Specialisation** lets you provide a custom version.

```cpp
template<typename T>
void serialize(T val) { /* generic */ }

template<>              // full specialisation for bool
void serialize<bool>(bool val) {
    std::cout << (val ? "true" : "false");
}
```

Partial specialisation applies to class templates and restricts one or more — but not all — type parameters.

## Variadic Templates (C++11)

Variadic templates accept an arbitrary number of type parameters. SystemC 2.3+ uses them internally for some port utilities. The pattern looks like:

```cpp
template<typename... Args>
void log(Args&&... args) {
    (std::cout << ... << args);   // C++17 fold expression
}
```

You rarely write these for everyday SystemC modeling, but you will encounter them when reading library headers.

## Common Pitfalls

- **Template definitions in headers** — the compiler needs the full template body at each point of instantiation. Putting the definition in a `.cpp` file causes linker errors. Almost all template code lives in `.h` files.
- **Long error messages** — a type mismatch in a template can produce dozens of lines of cryptic diagnostics. Read the *first* error carefully; the rest are cascades.
- **Implicit instantiation bloat** — if the same template is instantiated with many types across many translation units, compile times grow. Use **explicit instantiation declarations** (`extern template`) to share object code.

## Worked Example: Parameterisable Bus Monitor

```cpp
template<typename PAYLOAD, int WIDTH>
SC_MODULE(BusMonitor) {
    sc_in<sc_lv<WIDTH>>  bus;
    sc_in<bool>          valid;

    SC_CTOR(BusMonitor) {
        SC_METHOD(sample);
        sensitive << valid.pos();   // trigger on rising edge of valid
    }

    void sample() {
        if (valid.read()) {
            std::cout << sc_time_stamp()
                      << " BUS[" << WIDTH << "]="
                      << bus.read() << "\n";
        }
    }
};

// Instantiate for a 32-bit bus with a custom payload type
BusMonitor<MyPayload, 32> mon("mon");
```

> **Interview answer:** C++ templates generate type-safe, zero-overhead specialised code at compile time. SystemC uses them so that port and signal types carry the data type as a compile-time parameter, turning type-mismatch errors from silent runtime bugs into immediate compilation failures.
