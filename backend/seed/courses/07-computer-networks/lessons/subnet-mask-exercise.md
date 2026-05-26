# Exercise: Subnet Mask Converter

Subnet masks and CIDR prefix lengths are two ways to express the same thing. Network engineers must be fluent in converting between them — when reading router configurations, firewall rules, and IPAM tools you'll encounter both forms.

## Background

A prefix length `/N` corresponds to a 32-bit subnet mask where the first N bits are 1 and the remaining 32-N bits are 0. Examples:

| Prefix | Binary mask | Dotted-decimal |
|--------|------------|----------------|
| /0  | 00000000.00000000.00000000.00000000 | 0.0.0.0 |
| /8  | 11111111.00000000.00000000.00000000 | 255.0.0.0 |
| /16 | 11111111.11111111.00000000.00000000 | 255.255.0.0 |
| /24 | 11111111.11111111.11111111.00000000 | 255.255.255.0 |
| /26 | 11111111.11111111.11111111.11000000 | 255.255.255.192 |
| /32 | 11111111.11111111.11111111.11111111 | 255.255.255.255 |

Valid subnet masks are always a contiguous block of 1s followed by 0s. A value like `255.255.128.255` is NOT a valid subnet mask, but you will not be given invalid inputs.

## Your Task

See the exercise prompt for the exact input/output specification.
