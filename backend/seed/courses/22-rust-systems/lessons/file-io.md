# File I/O and Standard I/O

Rust's `std::fs` and `std::io` modules give you the building blocks for reading files, writing files, and working with standard input and output.

## Reading a whole file

```rust
use std::fs;

let contents = fs::read_to_string("data.txt").expect("failed to read file");
println!("{}", contents);
```

`read_to_string` returns `io::Result<String>`. Use `.expect()` for quick scripts; in library code, propagate with `?`.

## Writing a file

```rust
use std::fs;

fs::write("output.txt", "hello world\n").expect("failed to write");
```

For appending or fine-grained control, use `OpenOptions`:

```rust
use std::fs::OpenOptions;
use std::io::Write;

let mut file = OpenOptions::new()
    .append(true)
    .create(true)
    .open("log.txt")
    .unwrap();

writeln!(file, "new log entry").unwrap();
```

## Buffered reading line by line

For large files, read line by line to avoid loading everything into memory:

```rust
use std::fs::File;
use std::io::{BufRead, BufReader};

let file = File::open("big.txt").unwrap();
let reader = BufReader::new(file);

for (i, line) in reader.lines().enumerate() {
    let line = line.unwrap();
    println!("{}: {}", i + 1, line);
}
```

`BufReader` wraps any `Read` and provides buffering plus the `lines()` iterator.

## Reading from stdin

```rust
use std::io::{self, BufRead};

let stdin = io::stdin();
for line in stdin.lock().lines() {
    let line = line.unwrap();
    println!("echo: {}", line);
}
```

For competitive-programming or exercise style (read entire stdin at once):

```rust
use std::io::{self, Read};

let mut input = String::new();
io::stdin().read_to_string(&mut input).unwrap();
let tokens: Vec<&str> = input.split_whitespace().collect();
```

## Writing to stdout / stderr

```rust
use std::io::{self, Write};

print!("no newline");
println!("with newline");

// stderr
eprintln!("error: something went wrong");

// Flushing (important before program exit in some cases)
io::stdout().flush().unwrap();
```

## Working with paths

Use `std::path::Path` and `PathBuf` instead of raw strings — they are cross-platform:

```rust
use std::path::{Path, PathBuf};

let path = Path::new("/tmp/data.txt");
println!("{:?}", path.extension());   // Some("txt")
println!("{:?}", path.file_name());   // Some("data.txt")
println!("{}", path.exists());         // true/false

// Building paths portably
let mut p = PathBuf::from("/tmp");
p.push("subdir");
p.push("file.txt");
// "/tmp/subdir/file.txt" on Unix, "\\tmp\\subdir\\file.txt" on Windows
```

## Directory operations

```rust
use std::fs;

fs::create_dir_all("a/b/c").unwrap();   // mkdir -p

for entry in fs::read_dir(".").unwrap() {
    let entry = entry.unwrap();
    println!("{:?}", entry.file_name());
}

fs::remove_file("tmp.txt").unwrap();
fs::remove_dir_all("a").unwrap();
```

## Error handling for I/O

`std::io::Error` carries an `ErrorKind` for programmatic inspection:

```rust
use std::fs;
use std::io::ErrorKind;

match fs::read_to_string("missing.txt") {
    Ok(content) => println!("{}", content),
    Err(e) if e.kind() == ErrorKind::NotFound => println!("file not found"),
    Err(e) => eprintln!("other error: {}", e),
}
```

Combining `?` with `main() -> Result<(), Box<dyn std::error::Error>>` lets you propagate I/O errors cleanly from `main`:

```rust
use std::fs;
use std::io;

fn main() -> Result<(), io::Error> {
    let data = fs::read_to_string("config.txt")?;
    println!("{}", data.trim());
    Ok(())
}
```
