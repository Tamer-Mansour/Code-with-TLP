# Subnet Mask Converter

Read a single line from standard input. It will be one of two forms:
1. A prefix length integer: `24` (meaning /24)
2. A dotted-decimal subnet mask: `255.255.255.0`

If the input is a plain integer (contains no dot), convert it to the dotted-decimal subnet mask and print:
```
Mask: <dotted-decimal>
```

If the input is a dotted-decimal mask (contains a dot), convert it to the prefix length and print:
```
Prefix: <integer>
```

Prefix lengths are in the range 0–32 inclusive.

## Examples

Input: `24`
Output: `Mask: 255.255.255.0`

Input: `255.255.255.0`
Output: `Prefix: 24`

Input: `26`
Output: `Mask: 255.255.255.192`

Input: `255.255.240.0`
Output: `Prefix: 20`

Input: `0`
Output: `Mask: 0.0.0.0`

Input: `255.255.255.255`
Output: `Prefix: 32`
