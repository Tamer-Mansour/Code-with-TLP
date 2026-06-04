# Unsafe Rust and Systems Interfaces

Safe Rust provides strong guarantees: no dangling pointers, no data races, no use-after-free. But some systems programming tasks require capabilities the borrow checker cannot verify. The `unsafe` keyword is the escape hatch — a promise from the programmer that the invariants are upheld manually.

## The Five Powers of `unsafe`

The `unsafe` keyword unlocks exactly five capabilities — nothing more:

1. **Dereference raw pointers** (`*const T` and `*mut T`)
2. **Call unsafe functions or methods** (including C FFI functions)
3. **Access or mutate static mutable variables** (`static mut`)
4. **Implement unsafe traits** (e.g., `Send`, `Sync`)
5. **Access fields of a `union`**

All other Rust safety guarantees remain in full force inside an `unsafe` block. Type safety, no null dereferences in safe code, no uninitialized reads — all still enforced.

## Raw Pointers

```rust
let mut x = 42_i32;
let ptr: *mut i32 = &mut x as *mut i32;

unsafe {
    // Dereferencing a raw pointer is unsafe: the compiler can't prove it's valid
    *ptr = 100;
    println!("{}", *ptr);   // 100
}
```

Raw pointers can be created in safe code; only dereferencing them requires `unsafe`.

## Calling Unsafe Functions

```rust
unsafe fn danger() {
    println!("I promise this is safe, but the compiler can't verify it.");
}

unsafe {
    danger();
}
```

## Safe Abstractions over Unsafe Code

The right pattern is to wrap unsafe code in a safe API:

```rust
pub fn split_at_mid(slice: &[i32], mid: usize) -> (&[i32], &[i32]) {
    let len = slice.len();
    let ptr = slice.as_ptr();
    assert!(mid <= len);
    unsafe {
        (
            std::slice::from_raw_parts(ptr, mid),
            std::slice::from_raw_parts(ptr.add(mid), len - mid),
        )
    }
}
```

The public function is safe; the `unsafe` block is an implementation detail. Users never have to write `unsafe` themselves.

## Foreign Function Interface (FFI)

Rust can call C functions through `extern` blocks:

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("abs(-7) = {}", abs(-7));   // 7
    }
}
```

The `"C"` ABI tells Rust to use the C calling convention. The `libc` crate provides type aliases matching C's types (`c_int`, `c_char`, etc.), and the `nix` crate wraps POSIX system calls in safe APIs.

## Memory Layout and `repr(C)`

Rust is free to reorder struct fields for optimal packing. To get a predictable, C-compatible layout, use `#[repr(C)]`:

```rust
#[repr(C)]
struct Point {
    x: f32,   // offset 0, size 4
    y: f32,   // offset 4, size 4
}             // total: 8 bytes
```

Without `#[repr(C)]`, the layout is unspecified and the compiler may add padding or reorder fields. With it, the layout matches what C would produce — essential for FFI.

### Alignment Rules

Each field is placed at an offset that is a multiple of the field's **alignment requirement**:

| Type | Size (bytes) | Alignment (bytes) |
|------|-------------|-------------------|
| `bool`, `u8`, `i8` | 1 | 1 |
| `u16`, `i16` | 2 | 2 |
| `u32`, `i32`, `f32` | 4 | 4 |
| `u64`, `i64`, `f64`, `usize` | 8 | 8 |

The struct's total size is padded to a multiple of its largest field alignment.

## `static mut` — Global Mutable State

```rust
static mut COUNTER: u32 = 0;

unsafe fn increment() {
    COUNTER += 1;   // unsafe: two threads could race here
}
```

`static mut` is almost never the right tool. Use `AtomicU32`, `Mutex`, or `OnceLock` instead for safe global state.

## Inline Assembly

For cases where you need to emit specific machine instructions:

```rust
use std::arch::asm;

unsafe {
    asm!(
        "mov {out}, {input}",
        input = in(reg) 42_u64,
        out = out(reg) _,
    );
}
```

Inline assembly is the last resort. Use it only for CPU-specific instructions not otherwise reachable from Rust or the OS API.

## Common `unsafe` Mistakes to Avoid

- **Creating two `&mut` references to the same data** — undefined behavior even in `unsafe` blocks; the aliasing rules still apply.
- **Using a raw pointer after the pointed-to value is freed** — use-after-free is still UB; `unsafe` doesn't make it safe, it just moves responsibility to you.
- **Calling FFI functions from multiple threads without synchronization** — C libraries rarely document their thread-safety; wrap them in a `Mutex`.
- **Forgetting padding in `repr(C)` structs** — when computing offsets manually, always account for alignment padding.

## Further Reading

- [The Rust Programming Language, Chapter 19.1](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html) — unsafe Rust overview
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) — the authoritative guide to unsafe Rust: memory layout, variance, FFI, atomics, and building sound safe abstractions
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — bare-metal and embedded systems chapters
