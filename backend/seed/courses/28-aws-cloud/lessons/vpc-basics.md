# VPC Basics

A **VPC** (Virtual Private Cloud) is your own private network inside AWS. You pick the IP range, slice it into subnets, control routing, and decide what's public vs private.

## The pieces

- **VPC** — has a CIDR block, e.g. `10.0.0.0/16` (65,536 IPs).
- **Subnet** — slice of the VPC, in one AZ. e.g. `10.0.1.0/24` in `us-east-1a`.
- **Route table** — per subnet, decides where traffic goes.
- **Internet gateway (IGW)** — public internet access.
- **NAT gateway** — egress-only internet from private subnets.
- **Security group (SG)** — stateful firewall on ENIs.
- **NACL** — stateless firewall on subnets (less commonly used).
- **VPC endpoint** — private access to AWS services without going through the internet.

## A standard topology

```
     Internet
        │
   ┌────▼─────┐
   │   IGW    │
   └────┬─────┘
        │
┌───────┼───────────────────────┐
│  VPC 10.0.0.0/16              │
│                               │
│  ┌─ public subnet ─────────┐  │
│  │ 10.0.1.0/24, az-a       │  │
│  │ ALB, NAT gateway        │  │
│  └─────────────────────────┘  │
│                               │
│  ┌─ private subnet ────────┐  │
│  │ 10.0.10.0/24, az-a      │  │
│  │ application instances   │  │
│  └─────────────────────────┘  │
│                               │
│  ┌─ data subnet ───────────┐  │
│  │ 10.0.20.0/24, az-a      │  │
│  │ RDS, ElastiCache        │  │
│  └─────────────────────────┘  │
│                               │
│   (repeat for az-b, az-c)     │
└───────────────────────────────┘
```

Three tiers per AZ, two or three AZs. Public-facing load balancer; private application instances; private database subnet with no internet route.

## Public vs private subnets

A **public** subnet has a route `0.0.0.0/0 → IGW`. Things in it can be reached from / reach the internet directly.

A **private** subnet has `0.0.0.0/0 → NAT gateway` (or no internet route at all). Things in it can reach out via NAT but can't be reached from the internet.

Run app and DB in **private** subnets. Only put load balancers, bastions, and NAT in public.

## Security groups

```
inbound:  TCP 443 from 0.0.0.0/0     (public ALB)
inbound:  TCP 80  from sg-app-tier   (only app tier can reach me)
outbound: TCP 443 to 0.0.0.0/0       (egress allowed)
```

**Stateful** — if you allow inbound, the response goes back automatically.

Best practice: use SG references (`sg-app-tier`) instead of CIDR blocks. The SG itself describes which resources can talk.

## CIDR planning

Plan your CIDRs **before** you create the VPC. Renaming subnets is impossible; renumbering is painful.

- VPC: `/16` (room for 64K IPs).
- Subnet per tier per AZ: `/24` (250 usable IPs) or `/22` for bigger.
- Reserve room for future regions and inter-VPC peering — don't overlap.

A common scheme:

```
prod         10.0.0.0/16
staging      10.1.0.0/16
dev          10.2.0.0/16
shared svcs  10.10.0.0/16
```

## NAT gateway costs

NAT gateways are AWS's quiet money pit: **per-hour fee + per-GB data processing**. A single NAT can rack up hundreds of dollars/month for a chatty workload.

Mitigations:

- **VPC endpoints** for S3, DynamoDB, and many other AWS services — traffic stays internal, free.
- **One NAT per VPC** instead of per-AZ (slight HA hit; massive cost saving for small environments).
- **NAT Instance** (an EC2 you maintain) for tiny dev environments.

## Connectivity beyond one VPC

- **VPC Peering** — direct 1:1 connection between two VPCs.
- **Transit Gateway** — hub-and-spoke for many VPCs and on-prem networks.
- **VPN** / **Direct Connect** — extend to your data center.
- **PrivateLink** — expose a service in your VPC to another VPC without peering.

Most multi-VPC architectures use **Transit Gateway**; it scales much better than full-mesh peering.
