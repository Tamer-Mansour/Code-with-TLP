# AWS Overview - Regions, Accounts, Console, CLI

AWS is Amazon's cloud platform. It offers 200+ services, but most workloads use a handful: compute, storage, database, networking, security.

## Geography

- **Region** — a geographic area (`us-east-1`, `eu-west-1`). Most services are region-scoped; data stays in the region unless you replicate.
- **Availability Zone (AZ)** — an isolated data center within a region. Always span 2–3 AZs for HA.
- **Edge locations** — CloudFront and Route 53 PoPs worldwide.

Pick a region close to your users. Watch out — service availability and pricing vary across regions.

## Accounts and Organizations

An **AWS account** is a billing + isolation boundary. Most companies have many accounts via **AWS Organizations** — separating dev, staging, prod, and per-team workloads.

- **AWS SSO / IAM Identity Center** — single sign-on across accounts.
- **Control Tower** — opinionated multi-account scaffolding.

A common pattern: 5+ accounts (root, audit, log archive, dev, staging, prod-each-region) with central SSO.

## Talking to AWS

Three interfaces:

- **Console** (web GUI). Good for exploring; bad for reproducibility.
- **CLI**:
  ```bash
  aws s3 ls
  aws ec2 describe-instances --region us-east-1
  ```
- **SDKs** (Python `boto3`, JS, Go, Java, .NET, etc.).

For real work: **infrastructure as code**. Console clicks should be rare and intentional.

## Infrastructure as Code

- **CloudFormation** — AWS's native YAML/JSON.
- **AWS CDK** — write infrastructure in Python/TypeScript/Go, compile to CloudFormation.
- **Terraform** — multi-cloud, the most popular.
- **Pulumi** — like CDK but multi-cloud.

For new projects: CDK or Terraform. CDK is closer to AWS; Terraform is more portable.

## Pricing

A few pricing patterns to internalize:

- **Compute** — pay per second (EC2, Fargate, Lambda).
- **Storage** — pay per GB-month (S3, EBS).
- **Network egress** — pay per GB out (cheap within region, painful cross-region or to the internet).
- **API calls** — many services charge per request (S3 PUT/GET, DynamoDB ops, Lambda invocations).

Cost surprises usually come from: data transfer between regions, NAT Gateway traffic, idle resources, RDS that's bigger than needed.

Always set up **Cost Explorer**, **Budgets** with alerts, and tag resources with `team` / `environment` / `project` for cost attribution.

## A first session

```bash
# install
brew install awscli           # or pip install awscli
# configure
aws configure                  # access key, secret, region

# something cheap
aws s3 mb s3://my-test-bucket-$RANDOM
aws s3 ls
aws ec2 describe-vpcs
```

For credentials in real projects: don't use long-lived IAM access keys. Use **SSO sessions** or **IAM roles** (we cover this in the IAM lesson).

## Mental model

AWS is "give me the building block I asked for, and bill me." It rarely tells you "the right way" to assemble them — that's up to you. Read the **Well-Architected Framework** for the official opinionated guidance.

## Free Tier

Most services have a free tier for the first 12 months (or always free for some). Great for learning. Watch the budget — accidental large costs are easy if you forget to terminate things.
