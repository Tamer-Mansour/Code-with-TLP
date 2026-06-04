# VPC Subnet Design Exercise

Subnet sizing is one of the first decisions you make when creating a VPC — and one of the hardest to change later. AWS does not let you resize a subnet after creation. Plan ahead.

## CIDR Notation Refresher

A CIDR block like `10.0.1.0/24` means:
- The first 24 bits are the **network prefix** (fixed): `10.0.1`
- The remaining 8 bits are the **host portion**: 2^8 = 256 addresses

AWS always reserves 5 addresses per subnet, leaving 251 usable for EC2 instances, RDS endpoints, Lambda ENIs, and other resources.

## The 5 Reserved Addresses

For subnet `10.0.1.0/24`:

| Address       | Role                  |
|---------------|-----------------------|
| 10.0.1.0      | Network address       |
| 10.0.1.1      | VPC router            |
| 10.0.1.2      | DNS resolver          |
| 10.0.1.3      | Future AWS use        |
| 10.0.1.255    | Broadcast (reserved)  |

This is why `/30` gives only 2 usable IPs, and `/28` (the smallest practical AWS subnet) gives 11.

## Sizing Strategy

A common production rule of thumb:

| Tier                | Prefix | Usable IPs | Rationale                              |
|---------------------|--------|------------|----------------------------------------|
| Public (ALB)        | /28    | 11         | ALB needs ~8 IPs; no instances here   |
| Private (app tier)  | /22    | 1019       | Room for many instances + scaling      |
| Data (RDS/ElastiCache) | /27 | 27         | Few endpoints, high availability       |

Always over-provision. You cannot expand a subnet's CIDR, but you can add a second subnet to the VPC later.

## Prefix Reference Table

| Prefix | Total IPs | Usable IPs |
|--------|-----------|------------|
| /28    | 16        | 11         |
| /27    | 32        | 27         |
| /26    | 64        | 59         |
| /25    | 128       | 123        |
| /24    | 256       | 251        |
| /23    | 512       | 507        |
| /22    | 1024      | 1019       |
| /21    | 2048      | 2043       |
| /20    | 4096      | 4091       |
| /19    | 8192      | 8187       |
| /16    | 65536     | 65531      |

## Avoiding Overlaps

When connecting VPCs (via VPC Peering or Transit Gateway) or extending to on-premises (via Direct Connect or VPN), overlapping CIDR blocks cause routing failures. Plan all address spaces centrally before deploying.

A common enterprise scheme:
```
10.0.0.0/8 — entire org
  10.0.0.0/16  — prod
  10.1.0.0/16  — staging
  10.2.0.0/16  — dev
  10.10.0.0/16 — shared services
```

## Exercise

In this exercise you will find the smallest subnet prefix that satisfies each workload's IP requirements. This directly maps to real VPC design decisions.

## Further Reading

- [VPC Subnets documentation](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html)
- [NIST SP 800-146](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-146.pdf) — covers cloud network isolation principles that make VPC subnet segmentation a security best practice, not just an operational one.
