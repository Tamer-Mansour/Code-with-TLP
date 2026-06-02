# Generic Payload Extensions

The TLM-2.0 generic payload covers the universal case — address, data, byte-enables. Real bus protocols like AXI4, CHI, or PCIe carry additional attributes: burst type, security domain, QoS priority, transaction ID, protection bits. Extensions allow you to attach protocol-specific metadata to a GP without breaking interoperability with models that do not understand those extras.

## The Extension Base Class

Every extension type derives from `tlm_extension`:

```cpp
template <typename T>
class tlm_extension : public tlm_extension_base {
public:
    virtual tlm_extension_base* clone() const = 0;
    virtual void copy_from(const tlm_extension_base&) = 0;
};
```

The template parameter `T` is the concrete extension type itself (CRTP). The framework uses this to generate a unique static ID per extension type automatically.

## Defining a Custom Extension

```cpp
// AXI4-specific attributes
struct Axi4Extension : public tlm::tlm_extension<Axi4Extension> {
    uint8_t  axid  = 0;    // Transaction ID
    uint8_t  axprot = 0;   // Protection bits (privilege / secure / instruction)
    uint8_t  axqos  = 0;   // Quality-of-Service priority (0–15)
    uint8_t  axcache = 0;  // Cache attributes

    tlm::tlm_extension_base* clone() const override {
        return new Axi4Extension(*this);  // deep copy
    }
    void copy_from(const tlm::tlm_extension_base& other) override {
        *this = static_cast<const Axi4Extension&>(other);
    }
};
```

## Attaching and Reading an Extension

```cpp
// Initiator: attach before calling b_transport
Axi4Extension* ext = new Axi4Extension;
ext->axid   = 3;
ext->axprot = 0x2;  // non-secure, privileged
ext->axqos  = 8;
trans.set_extension(ext);  // GP now owns the extension

// Target: read and process
Axi4Extension* rx_ext = nullptr;
trans.get_extension(rx_ext);
if (rx_ext) {
    if (rx_ext->axprot & 0x2)  // secure access check
        grant_access();
}
```

`set_extension` overwrites any previously set extension of the same type. `get_extension` returns `nullptr` if no extension of that type is attached — targets must always check for null before dereferencing.

## Extension Ownership and Memory Management

- `set_extension(T* ext)` — GP takes ownership; it will call `delete` when the GP is destroyed.
- `set_auto_extension(T* ext)` — same semantics, but `clone()` is called automatically when the GP is copied through a passthrough socket. Prefer this for AT models where the GP may travel through many sockets.
- `clear_extension<T>()` — removes and deletes the extension.
- `release_extension<T>()` — removes the extension and returns the pointer without deleting; caller becomes owner.

```cpp
// Safe idiom: use set_auto_extension so cloning is automatic
trans.set_auto_extension(new Axi4Extension{.axid=1, .axqos=4});
```

## Interoperability Rule

Extensions are optional by definition. A well-written target must function correctly even when an expected extension is absent — it should fall back to a default behavior or ignore the field:

```cpp
// Interoperable target
Axi4Extension* ext = nullptr;
trans.get_extension(ext);
uint8_t qos = ext ? ext->axqos : 0;  // default QoS = 0 if not present
schedule_with_priority(qos);
```

This is the fundamental rule that keeps TLM-2.0 interoperability intact: extensions enrich, they do not mandate.

## Worked Example: Security Filter

```cpp
// Interconnect snoops the extension and blocks non-secure accesses
tlm::tlm_sync_enum SecureFilter::nb_transport_fw(
        tlm::tlm_generic_payload& trans,
        tlm::tlm_phase& phase,
        sc_core::sc_time& t) {
    Axi4Extension* ext = nullptr;
    trans.get_extension(ext);
    bool is_secure = ext && (ext->axprot & 0x2);

    if (!is_secure && secure_only_region(trans.get_address())) {
        trans.set_response_status(tlm::TLM_GENERIC_ERROR_RESPONSE);
        phase = tlm::BEGIN_RESP;
        return tlm::TLM_UPDATED;
    }
    return target_socket->nb_transport_fw(trans, phase, t);
}
```

## Common Pitfalls

- **Forgetting `clone()` in AT models** — without a correct `clone()`, a GP passed through a passthrough socket silently drops the extension in the copy.
- **Double-delete** — calling both `clear_extension` and destroying the GP leads to double-delete; let the GP manage lifetime.
- **Casting without null check** — `static_cast` on a null extension pointer is undefined behavior; always check `get_extension` return before use.

> **Interview answer:** TLM-2.0 extensions are protocol-specific structs derived from `tlm_extension<T>` that attach to a generic payload via `set_extension()`; targets that do not understand an extension should check for null and fall back gracefully — preserving interoperability while allowing AXI, CHI, and other protocol attributes to travel through the same socket.
