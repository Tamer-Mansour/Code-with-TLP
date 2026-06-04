# Exercise: TLM Generic Payload Decoder

## Problem Statement

The TLM-2.0 generic payload is the standard transaction object passed between initiators and targets over sockets. It contains: command (`READ` or `WRITE`), address (unsigned integer), data length in bytes, and response status.

Valid response statuses are: `OK`, `ADDRESS_ERROR`, `COMMAND_ERROR`, `BURST_ERROR`, `BYTE_ENABLE_ERROR`, `GENERIC_ERROR`.

Given N transactions, each described as `<command> <address> <data_length>`, validate and decode them:

- Command must be `READ` or `WRITE` (case-sensitive)
- Address must be a non-negative integer
- Data length must be a positive integer (1 to 64 bytes inclusive)

If valid, print: `VALID: <command> @ 0x<address_hex_uppercase> len=<data_length>`

If command is invalid, print: `ERROR: COMMAND_ERROR`

If address is negative, print: `ERROR: ADDRESS_ERROR`

If data_length < 1 or > 64, print: `ERROR: BURST_ERROR`

Check in the order: command, then address, then data_length.

## Input Format

- First line: integer `N` (1 <= N <= 20)
- Next N lines: `<command> <address> <data_length>`

## Output Format

- N lines, one per transaction

## Constraints

- 1 <= N <= 20
- Addresses fit in a 32-bit unsigned integer (when valid)
- Data lengths are integers

## Sample Input

```
4
READ 256 4
WRITE 4096 8
INVALID 0 4
READ 128 0
```

## Sample Output

```
VALID: READ @ 0x100 len=4
VALID: WRITE @ 0x1000 len=8
ERROR: COMMAND_ERROR
ERROR: BURST_ERROR
```

## Additional Example

Input:
```
3
WRITE 65536 16
READ 0 65
READ 0 1
```

Output:
```
VALID: WRITE @ 0x10000 len=16
ERROR: BURST_ERROR
VALID: READ @ 0x0 len=1
```
