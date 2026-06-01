# IAM - Users, Roles, Policies

IAM (Identity and Access Management) controls **who can do what** in AWS. Get IAM right and a leaked credential is a contained problem; get it wrong and one mistake is catastrophic.

## The pieces

- **User** — long-lived identity for a human. Has access keys / console login.
- **Group** — bag of users. Permissions attached to the group cascade.
- **Role** — temporary identity assumed by something (an EC2 instance, a Lambda, another account).
- **Policy** — JSON document of permissions: allow or deny which actions on which resources.

## Don't use IAM users for humans

Modern AWS guidance: use **IAM Identity Center** (formerly SSO) for human access. Users get a single login, AWS issues short-lived credentials per session. No long-lived access keys to leak.

IAM users still make sense for:

- CI/CD systems that can't use OIDC.
- Legacy integrations.
- The first emergency-break-glass user.

Even then, **use roles wherever possible**. EC2/Lambda/ECS can assume a role automatically — no static credentials needed.

## A policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    }
  ]
}
```

`Effect`, `Action`, `Resource`. Add `Condition` for fine-grained rules (e.g., only from a specific VPC, only with MFA, only during business hours).

## Evaluation logic

1. **Explicit Deny** — wins. Always.
2. **Explicit Allow** — required for an action.
3. **Default Deny** — if nothing allows it.

Bucket policies, IAM policies, SCPs, permissions boundaries all combine. Read the **policy evaluation logic** docs once carefully; refer back when debugging "why can't I do this."

## Roles for AWS services

```
EC2 instance  ──► instance profile ──► Role ──► S3 read
Lambda        ──► execution role  ──► Role ──► DynamoDB read+write
ECS task      ──► task role       ──► Role ──► Secrets Manager read
```

The service automatically assumes the role and gets temporary credentials. Your code calls `aws s3` without ever seeing a key.

## Cross-account access

A role in account B can be assumed by users/roles in account A:

```json
// trust policy on the role in account B
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::ACCOUNT_A:root" },
    "Action": "sts:AssumeRole"
  }]
}
```

From account A:

```bash
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT_B:role/MyRole --role-session-name s
```

The right pattern for shared services, audit access, multi-account deployments.

## OIDC for CI/CD

GitHub Actions, GitLab, etc. can assume an IAM role without storing AWS keys:

```yaml
# .github/workflows/deploy.yml
permissions:
  id-token: write
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubDeploy
      aws-region: us-east-1
```

Configure the IAM role to trust your GitHub repo's OIDC provider. No more long-lived secrets in CI.

## Permission boundaries and SCPs

- **Permission boundary** — a ceiling on what a user/role can do, regardless of attached policies.
- **Service Control Policy (SCP)** — set at the Organization level; applies to entire accounts.

Useful for "no one in this account can touch IAM" or "no resources outside our approved regions."

## Best practices

- Root account: enable MFA, lock it away, never use it.
- Every identity has MFA.
- Least privilege — start narrow, broaden as needed.
- Use **AWS IAM Access Analyzer** to find overly-broad policies.
- Tag-based access (`aws:ResourceTag/team`) for fine-grained authorization at scale.
