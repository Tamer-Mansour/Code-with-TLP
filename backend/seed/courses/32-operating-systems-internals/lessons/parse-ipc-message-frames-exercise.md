# Exercise: Parse Length-Prefixed IPC Message Frames

Real IPC channels — Unix domain sockets, TCP connections, named pipes — are byte streams with no inherent message boundaries. When you send two messages back-to-back, the reader may receive them in one chunk, two chunks, or split across three reads. To delineate messages, virtually every protocol adds **framing**.

The simplest and most common framing scheme is the **length-prefix** (also called TLV — Type-Length-Value, or just LV when type is implicit):

```
+------------------+-------------------------------+
|  4-byte length   |  <length> bytes of payload    |
|  (big-endian)    |  (UTF-8 message text)         |
+------------------+-------------------------------+
```

The receiver reads exactly 4 bytes to learn the payload size, then reads exactly that many more bytes to get the message. This works regardless of how the underlying stream fragments the data.

## What You Will Implement

Write a Python program that reads a stream of bytes encoded as space-separated decimal integers (0–255) on a single line of stdin, then parses every length-prefixed frame it contains and prints each payload message on its own line.

### Rules

1. The 4-byte length header is **big-endian unsigned int** (network byte order).
2. The payload bytes represent a UTF-8 string — decode and print it.
3. Input is guaranteed to contain one or more complete, valid frames.
4. There will be no trailing bytes after the last frame.
5. If the stream contains zero frames (empty input or all whitespace), print nothing.

### Example

For the message `"hello"` (5 bytes: `h e l l o` = `104 101 108 108 111`), the frame is:

```
0 0 0 5 104 101 108 108 111
```

Header `0 0 0 5` = length 5, followed by 5 payload bytes.

### Skills This Exercises

- Big-endian integer decoding (as used in all network protocols).
- Incremental/stateful byte-stream parsing (the core skill for IPC and networking code).
- Understanding why byte streams need explicit framing — the fundamental lesson of this module.
