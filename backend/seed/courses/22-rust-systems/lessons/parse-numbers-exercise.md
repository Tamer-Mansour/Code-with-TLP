# Parse Sum

The Rust idiom for a fallible parse-and-sum:

```rust
fn parse_sum(input: &str) -> Result<i64, String> {
    let mut total = 0;
    for token in input.split_whitespace() {
        let n: i64 = token.parse().map_err(|_| format!("ERROR {}", token))?;
        total += n;
    }
    Ok(total)
}
```

Implement the equivalent in Python: print the sum on success, or `ERROR <token>` on the first failure.

See the prompt for I/O.
