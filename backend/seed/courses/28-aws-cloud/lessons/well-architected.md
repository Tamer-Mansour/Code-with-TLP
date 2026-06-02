# The AWS Well-Architected Framework

The **AWS Well-Architected Framework** is AWS's official guide for building secure, reliable, and cost-effective systems. It defines six pillars and hundreds of best practices. Every AWS Solutions Architect exam references it; every production architecture review should too.

## The Six Pillars

| Pillar                     | Core question                                      |
|----------------------------|----------------------------------------------------|
| Operational Excellence     | Can we run and improve over time?                  |
| Security                   | Is data and the system protected?                  |
| Reliability                | Does it recover from failure?                      |
| Performance Efficiency     | Are we using resources efficiently?                |
| Cost Optimization          | Are we paying for what we actually need?           |
| Sustainability             | Are we minimizing environmental impact?            |

## 1. Operational Excellence

- **Infrastructure as Code** — CloudFormation, CDK, or Terraform. Nothing created manually.
- **Runbooks and playbooks** — documented procedures for common and emergency operations.
- **Small, frequent changes** — deploy often, catch problems early.
- **Anticipate failure** — game days, chaos engineering.

Key services: CodePipeline, CloudFormation, Systems Manager (SSM) for parameter store and patch manager.

## 2. Security

- **Apply least privilege** — minimize IAM permissions.
- **Enable traceability** — CloudTrail for API calls, VPC Flow Logs for network.
- **Protect data in transit and at rest** — TLS everywhere, KMS encryption.
- **Prepare for incidents** — have an incident response plan before you need it.

Key services: IAM, KMS, Secrets Manager, GuardDuty, Security Hub, Inspector.

## 3. Reliability

- **Recover from failure automatically** — health checks, auto scaling, multi-AZ.
- **Test recovery procedures** — actually run a failover drill; don't assume it works.
- **Scale horizontally** — more small resources, not one giant one.
- **Manage change** — IaC, tested changes, rollback capability.

```
              ┌──────────────────────────────────────┐
              │         Multi-AZ architecture          │
              │  AZ-a         AZ-b         AZ-c        │
              │  app tier     app tier     app tier    │
              │  db standby   db primary   db standby  │
              └──────────────────────────────────────┘
```

Key services: ELB, Auto Scaling, Route 53 health checks, RDS Multi-AZ.

## 4. Performance Efficiency

- **Choose the right resource type** — don't use a general-purpose instance for a memory-heavy workload.
- **Go global in minutes** — CloudFront, Global Accelerator, Route 53.
- **Experiment with serverless** — remove the need to manage and tune servers.
- **Use purpose-built databases** — relational for OLTP, DynamoDB for key-value, ElastiCache for cache.

Key services: CloudFront, Lambda, Aurora, ElastiCache, Graviton EC2.

## 5. Cost Optimization

- **Adopt a consumption model** — pay for what you use; shut down what you don't.
- **Measure efficiency** — cost per business transaction, not just total AWS bill.
- **Use managed services** — DynamoDB, Lambda, Fargate cost more per unit but eliminate ops overhead.
- **Reserved capacity** — Savings Plans for steady-state compute.

Cost leaks to watch for:
- NAT Gateway data processing fees.
- EBS volumes attached to terminated instances.
- Idle EC2 instances (use AWS Cost Explorer + right-sizing recommendations).
- Unnecessary cross-region data transfer.

Key services: Cost Explorer, Budgets, Compute Savings Plans, Trusted Advisor.

## 6. Sustainability

- **Maximize utilization** — idle resources waste energy.
- **Use managed services** — AWS runs them at higher density than individual teams can.
- **Pick the right region** — some regions run on more renewable energy.
- **Graviton instances** — ARM-based, 60% more energy efficient for the same performance.

## The Well-Architected Tool

AWS provides a free tool in the console to review your architecture against these pillars:

1. Define a workload.
2. Answer a series of questions per pillar.
3. Get a report with High/Medium/Low risk findings and recommended improvements.

Run a Well-Architected review before each production launch and annually for existing systems.

## Mental shortcut: the three non-negotiables

If you had to pick three practices that apply to every system:

1. **Multi-AZ** — single AZ = single point of failure.
2. **Least-privilege IAM** — no `*` actions, no root in daily use.
3. **Infrastructure as Code** — if it's not in code, it doesn't exist.

Everything else in the framework builds on these fundamentals.
