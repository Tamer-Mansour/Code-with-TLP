# Designing a Minimal, Hard-to-Misuse Class API

A good class API is **discoverable, hard to use wrong, and easy to use right**. Scott Meyers called this "make interfaces easy to use correctly and hard to use incorrectly." In systems code, an API mistake can mean a dangling interrupt handler or a double-freed DMA buffer — so API clarity is safety-critical.

## Principle 1: Make Invalid States Unrepresentable

If the type system can rule out bad inputs, the programmer cannot accidentally pass them.

```cpp
// Bad: accepts any int, callee must validate
void set_priority(int p);

// Better: strong typedef rejects the wrong kind of int at compile time
enum class Priority : int { Low = 0, Normal = 1, High = 2, Realtime = 3 };
void set_priority(Priority p);
```

Calling `set_priority(42)` now fails to compile. No runtime check needed.

## Principle 2: Minimise the Public Surface

Every public method is a commitment you cannot easily break. Start private; promote to public only when a genuine caller exists.

Good questions to ask for each candidate method:
- Is this used by at least one external caller today?
- Does exposing it require revealing implementation details?
- Can the caller achieve the same goal by composing existing methods?

```cpp
class SpiDevice {
public:
    bool open(const char* dev, int freq_hz);
    void close();
    bool transfer(const uint8_t* tx, uint8_t* rx, size_t len);

    // NOT public: callers do not need to know about chip-select internals
    // void assert_cs();
    // void deassert_cs();
};
```

## Principle 3: Use the Type System to Encode Preconditions

```cpp
// Ambiguous: which argument is width, which is height?
Widget create_widget(int, int);

// Self-documenting: swapping arguments is a compile error
struct Width  { int value; };
struct Height { int value; };
Widget create_widget(Width w, Height h);
```

Tiny wrapper types eliminate whole classes of argument-order bugs with zero runtime cost.

## Principle 4: Prefer Verbs to Noun/Getter Pairs

"Tell, don't ask" — push behaviour into the class instead of pulling data out and computing externally.

```cpp
// Ask style: caller does the work; fragile if logic is spread around
if (buffer.get_size() > buffer.get_capacity() - buffer.get_reserved())
    buffer.set_size(buffer.get_capacity() - buffer.get_reserved());

// Tell style: one method, one responsibility
buffer.trim_to_capacity();
```

## Principle 5: Make Ownership Explicit

Use RAII types (`unique_ptr`, `shared_ptr`, custom handles) so ownership transfer is visible in the function signature.

```cpp
// Unclear: who frees this pointer?
Sensor* open_sensor(int id);

// Clear: caller owns the resource
std::unique_ptr<Sensor> open_sensor(int id);
```

## Principle 6: Design for the Common Case, Allow the Rare Case

Default parameters and factory functions can give sensible defaults while still allowing customisation:

```cpp
class Logger {
public:
    static Logger create(const char* path,
                         int level    = LOG_INFO,
                         bool flush   = false);
    // ...
};

// Common: one argument
auto log = Logger::create("/var/log/app.log");

// Rare: full control
auto debug_log = Logger::create("/tmp/debug.log", LOG_DEBUG, true);
```

## Worked Example: DMA Transfer API

```cpp
// Hard to misuse: buffer ownership is explicit,
// callback captures lifetime, enum prevents magic numbers
enum class DmaDir { MemToPeripheral, PeripheralToMem };

class DmaChannel {
public:
    using Callback = std::function<void(bool ok)>;

    // Transfer takes ownership of the buffer for the duration
    bool start(std::unique_ptr<uint8_t[]> buf,
               size_t                     len,
               DmaDir                     dir,
               Callback                   on_complete);

    void cancel();
    bool is_busy() const;

private:
    // hardware registers, IRQ number, etc.
};
```

A caller that forgets `DmaDir` gets a compile error. A caller that forgets the callback parameter gets a compile error. The buffer is owned by the transfer, so use-after-free is prevented by construction.

## Quick Checklist

- [ ] Public methods represent domain verbs, not data accessors
- [ ] No raw owning pointers in the public interface
- [ ] Argument types encode meaning (no `bool` / `int` ambiguity)
- [ ] Invalid combinations are either compile errors or factory failures
- [ ] The smallest possible surface area

## Interview Answer

> "A minimal, hard-to-misuse API makes invalid states unrepresentable — using strong types, RAII, and factory functions — exposes only the operations callers actually need, and uses verbs rather than data accessors to preserve the class invariant and reduce coupling."
