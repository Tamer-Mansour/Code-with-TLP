# CIDR Overlap Check

A common operational question: do two VPC CIDR blocks overlap? If they do, you can't peer them or route between them without conflict.

A CIDR block has an IP and a prefix length, e.g. `10.0.0.0/16` covers `10.0.0.0` through `10.0.255.255`. Two blocks overlap if their integer ranges intersect.

In this exercise you'll implement that check.

See the prompt.
