# EC2, EBS, and S3

## EC2 — Elastic Compute Cloud

Virtual machines. You pick:

- **Instance type** — family + size. `t3.small`, `m5.xlarge`, `c7g.large`. Different families optimize for CPU, memory, network, or GPU.
- **AMI** — the OS image. Amazon Linux 2023, Ubuntu, Windows.
- **VPC + subnet** — networking placement.
- **Security group** — virtual firewall.
- **IAM role** — what the instance can do in AWS.

Launch via the Console, CLI, or IaC:

```bash
aws ec2 run-instances \
  --image-id ami-xxx \
  --instance-type t3.micro \
  --key-name my-key \
  --subnet-id subnet-xxx \
  --security-group-ids sg-xxx \
  --iam-instance-profile Name=my-role-profile
```

## Pricing modes

- **On-Demand** — full price, pay per second.
- **Reserved Instances** / **Savings Plans** — commit to 1 or 3 years for 30–70% off.
- **Spot** — bid for unused capacity, 60–90% off, but can be reclaimed with 2 minutes' notice. Great for batch and stateless work.

For most workloads, **Savings Plans** are the right default. Use Spot for fault-tolerant work like CI, batch ML training.

## When EC2 is the right answer

- You need full OS control.
- Legacy software that wants a server, not a container.
- High-performance workloads with specific tuning.

For most new services, reach for **Fargate** (containers, no servers to manage) or **Lambda** (functions).

## EBS — block storage

Persistent disks attached to EC2 instances.

- **gp3** — general purpose SSD. The default. Pay for size + extra throughput/IOPS independently.
- **io2** — high-IOPS SSD for databases.
- **st1** — cheap throughput-optimized HDD for big sequential reads.

```bash
aws ec2 create-volume --availability-zone us-east-1a --size 100 --volume-type gp3
aws ec2 attach-volume --instance-id i-xxx --volume-id vol-xxx --device /dev/sdf
```

EBS volumes survive instance termination if `DeleteOnTermination` is false. Snapshot regularly:

```bash
aws ec2 create-snapshot --volume-id vol-xxx --description "daily backup"
```

## S3 — Simple Storage Service

Object storage. Buckets → objects (key + value). Designed for 11 nines of durability and massive scale.

```bash
aws s3 mb s3://my-bucket
aws s3 cp local.txt s3://my-bucket/path/file.txt
aws s3 sync ./build s3://my-bucket/
aws s3 ls s3://my-bucket/path/
```

### Storage classes

| Class                | Use case                            | Cost   |
|----------------------|-------------------------------------|--------|
| Standard             | Hot data                            | $$$$   |
| Standard-IA          | Infrequent access, 30+ day storage  | $$     |
| One Zone-IA          | Reproducible IA                     | $      |
| Glacier Instant      | Archive with instant retrieval      | $      |
| Glacier Flexible     | Archive, minutes to hours retrieval | ¢      |
| Glacier Deep Archive | Cold archive, hours to retrieve     | ¢¢     |

Use **lifecycle rules** to transition objects automatically (e.g., after 30 days move to IA, after 180 to Glacier).

### S3 security checklist

- **Block Public Access** at the account level (on by default for new accounts since 2023).
- **No bucket policies grant `*` principal** unless you really mean public.
- **Encrypt** with SSE-S3 or SSE-KMS (free, on by default).
- **Versioning** — recover from overwrites/deletes.
- **MFA Delete** for ultra-critical buckets.
- **Access logging** to a separate audit bucket.

### S3 as a website

Static site hosting is a built-in feature. Pair with CloudFront for HTTPS + caching.

```bash
aws s3 website s3://my-site --index-document index.html
```

For most production sites, use **CloudFront in front of S3**, not S3 website directly — CloudFront gives HTTPS, edge caching, and integration with WAF.
