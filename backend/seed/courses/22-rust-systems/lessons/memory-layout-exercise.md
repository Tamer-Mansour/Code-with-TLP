# Memory Layout Calculator

## Exercise Overview

When writing systems code in Rust — especially FFI with C, implementing allocators, or working with hardware memory maps — you need to know exactly how a struct is laid out in memory.

Rust's default layout algorithm applies **alignment padding**: each field is placed at an offset that is a multiple of the field's alignment requirement. The struct's total size is then padded to a multiple of its largest field alignment.

## Layout Algorithm

Given a list of fields in order:

1. Start with `current_offset = 0` and `max_align = 1`.
2. For each field:
   - Round `current_offset` up to the next multiple of the field's alignment.
   - Record this as the field's offset.
   - Add the field's size to `current_offset`.
   - Update `max_align = max(max_align, field_alignment)`.
3. Round `current_offset` up to the next multiple of `max_align` — this is the struct's total size.

## Example

```
Fields: flag (bool), value (u32), count (u64), short (u16)
```

| Step | Field | Alignment | Offset calculation | Offset |
|------|-------|-----------|-------------------|--------|
| 1 | flag (bool) | 1 | 0 rounds up to 0 | 0 |
| 2 | value (u32) | 4 | 1 rounds up to 4 | 4 |
| 3 | count (u64) | 8 | 8 rounds up to 8 | 8 |
| 4 | short (u16) | 2 | 16 rounds up to 16 | 16 |

After all fields: `current_offset = 18`. Max alignment = 8. Round 18 up to next multiple of 8 = **24**.

## Primitive Type Reference

| Type | Size (bytes) | Alignment (bytes) |
|------|-------------|-------------------|
| `bool`, `u8`, `i8` | 1 | 1 |
| `u16`, `i16` | 2 | 2 |
| `u32`, `i32`, `f32` | 4 | 4 |
| `u64`, `i64`, `f64`, `usize` | 8 | 8 |

## Study Resources

- [The Rustonomicon: Data Layout](https://doc.rust-lang.org/nomicon/data.html) — official deep-dive into Rust's memory layout rules, `repr(C)`, alignment, and padding
- [The Rust Programming Language, Chapter 19](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html) — unsafe Rust and FFI
- [Comprehensive Rust](https://google.github.io/comprehensive-rust/) — bare-metal and embedded chapters covering memory layout
