# Prompt: Parse Length-Prefixed IPC Message Frames

## Background

When processes communicate over a byte-stream channel (pipe, socket, FIFO), the stream carries no inherent message boundaries. A 4-byte **big-endian length prefix** before each payload is the standard way to frame messages, used in HTTP/2, gRPC, Redis RESP3, and virtually every custom IPC protocol.

## Task

Read a stream of bytes from stdin — given as space-separated decimal integers on a single line — and parse all length-prefixed frames. Print each frame's payload as a UTF-8 string, one per line.

## Input Format

- A single line containing space-separated integers in the range `[0, 255]`.
- The integers represent the raw byte stream.
- The stream consists of one or more contiguous frames.
- Each frame: **4 bytes (big-endian uint32 length)** followed by exactly `length` payload bytes.
- Input may also be an empty line, meaning zero frames — print nothing in that case.

## Output Format

- One line of output per frame, in order.
- Each line is the UTF-8 decoded payload string.
- No trailing spaces. Each line ends with a newline character.

## Constraints

- Total byte stream length: `0 ≤ N ≤ 10,000` bytes.
- Individual message payload: `0 ≤ L ≤ 9,996` bytes (length field value).
- Input is always valid (no truncated frames, no invalid UTF-8).
- No third-party libraries. Use Python standard library only.

## Sample Input

```
0 0 0 5 104 101 108 108 111 0 0 0 5 119 111 114 108 100
```

## Sample Output

```
hello
world
```

## Explanation

- Bytes `0 0 0 5` → length = 5.
- Next 5 bytes `104 101 108 108 111` → `"hello"`.
- Bytes `0 0 0 5` → length = 5.
- Next 5 bytes `119 111 114 108 100` → `"world"`.

## Notes

- Use `int.from_bytes(...)` with `byteorder='big'` to decode the 4-byte header.
- The payload bytes decode to ASCII/UTF-8 strings for all test cases.
- An empty or whitespace-only input line should produce no output.
