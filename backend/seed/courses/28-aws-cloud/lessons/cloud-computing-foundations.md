# Cloud Computing Foundations

Before using AWS effectively, you need a precise vocabulary. The definitions that follow come from [NIST Special Publication 800-145](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-145.pdf) — the canonical, vendor-neutral cloud computing reference used in every AWS certification program.

## The NIST Five Essential Characteristics

NIST defines cloud computing as a model that exhibits five characteristics:

| Characteristic            | What It Means in Practice                                           |
|---------------------------|---------------------------------------------------------------------|
| On-demand self-service    | Spin up an EC2 instance at midnight without calling anyone          |
| Broad network access      | Access resources over standard protocols from any device            |
| Resource pooling          | AWS's hardware serves many tenants; you get a logical slice         |
| Rapid elasticity          | Scale from 1 to 1000 instances in minutes; release just as fast     |
| Measured service          | You pay exactly for what you use (per-second billing for EC2)       |

**Rapid elasticity** is why Auto Scaling Groups and Lambda exist — the cloud is only valuable if you can consume and release capacity programmatically.

## Service Models: IaaS, PaaS, SaaS

```
            ┌──────────────────────────────┐
SaaS        │  Application                 │  Customer uses the app
            ├──────────────────────────────┤
PaaS        │  Platform / Runtime          │  Customer writes code
            ├──────────────────────────────┤
IaaS        │  Infrastructure (VMs, storage│  Customer manages OS up
            ├──────────────────────────────┤
            │  Virtualization / Hardware   │  AWS manages always
            └──────────────────────────────┘
```

| Model | AWS Examples                     | You Manage              |
|-------|----------------------------------|-------------------------|
| IaaS  | EC2, EBS, VPC                    | OS, runtime, app, data  |
| PaaS  | Elastic Beanstalk, Lambda, RDS   | App code and data       |
| SaaS  | WorkMail, Chime, QuickSight      | Just usage              |

The higher up the stack, the less you manage and the more AWS handles — but also the less control you have.

## Deployment Models

| Model      | Who Uses It                              | AWS Mapping                    |
|------------|------------------------------------------|--------------------------------|
| Public     | Anyone on the internet                   | Standard AWS                   |
| Private    | Single organization, own infrastructure  | AWS Outposts, VPC-only         |
| Hybrid     | Mix of public cloud + on-premises        | Direct Connect, Storage Gateway|
| Community  | Shared by orgs with common concerns      | GovCloud for US federal        |

Most applications use the **hybrid** model in practice: a public AWS environment connected to an on-premises data center via Direct Connect or VPN.

## AWS Global Infrastructure

AWS's physical presence is organized in three tiers:

- **Region** — a named geographic area (e.g., `us-east-1`, `eu-west-2`). Each region is fully independent with its own services, pricing, and data residency guarantees. Data does not leave a region unless you explicitly configure replication.
- **Availability Zone (AZ)** — one or more discrete, isolated data centers within a region, connected by high-speed private fiber. Each region has 2–6 AZs. Designing across 2+ AZs eliminates single data-center risk.
- **Edge Location** — a CloudFront Point of Presence (PoP) that caches content closer to end users. There are 400+ globally, far more than the ~35 regions.

```
Region: us-east-1
  ├── AZ: us-east-1a  (data center cluster A)
  ├── AZ: us-east-1b  (data center cluster B)
  └── AZ: us-east-1c  (data center cluster C)

Edge locations: New York, Chicago, Atlanta, Miami, ... (many cities)
```

## The AWS Shared Responsibility Model

This is one of the most tested concepts in AWS certifications:

- **AWS** is responsible for security **OF** the cloud — physical facilities, hardware, hypervisors, and managed service internals.
- **You** are responsible for security **IN** the cloud — OS patching on EC2, IAM configuration, security group rules, application code, encryption keys, and data.

The boundary shifts by service model:
- **EC2 (IaaS)** — you patch the OS.
- **RDS (PaaS)** — AWS patches the DB engine; you configure backups and encryption.
- **Lambda (PaaS/FaaS)** — AWS manages the runtime; you write secure code.

A critical misconception: **AWS does not automatically back up EC2 instances or EBS volumes.** Backup is always the customer's responsibility. Services like AWS Backup and RDS automated backups must be explicitly enabled.

## AWS Free Tier

AWS offers three kinds of free usage:

| Type              | Example                              | Duration     |
|-------------------|--------------------------------------|--------------|
| Always Free       | Lambda 1M requests/month             | Permanent    |
| 12-Month Free     | EC2 t3.micro 750 hrs/month           | First year   |
| Short-Term Trial  | Amazon Redshift 2-month trial        | Limited time |

**Important**: The 750 EC2 hours are shared across all running instances. Two t3.micro instances running simultaneously consume 1,500 hours and will incur charges. Always set up **AWS Budgets** with an email alert on your first day.

## Further Reading

- [NIST SP 800-145](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-145.pdf) — Full, 7-page definition of cloud computing. Free, public domain, authoritative.
- [NIST SP 800-146](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-146.pdf) — Cloud Computing Synopsis and Recommendations: deeper guidance on risks, security considerations, and deployment decisions.
