# IAM Advanced - Policies, Roles, and Least Privilege

Once you can log in and create users, the next step is mastering the IAM policy language and understanding how roles allow AWS services to act on your behalf.

## How IAM Evaluates a Request

Every API call goes through this decision tree:

1. Is this the **root account** or has **root MFA** approved it? → always allow (with exceptions).
2. Is there an explicit **Deny** in any attached policy? → deny immediately.
3. Is there an explicit **Allow** in any attached policy? → allow.
4. Default: **implicitly deny**.

"Deny overrides Allow" is the cardinal rule.

## Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnProd",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::prod-bucket",
        "arn:aws:s3:::prod-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

| Field       | Purpose                                          |
|-------------|--------------------------------------------------|
| `Sid`       | Optional human-readable identifier               |
| `Effect`    | `Allow` or `Deny`                                |
| `Action`    | Service prefix + action (e.g., `s3:GetObject`)   |
| `Resource`  | ARN of the resource, or `*`                      |
| `Condition` | Optional extra constraints (IP, time, tags, MFA) |

## Types of Policies

- **Identity-based** — attached to a user, group, or role.
- **Resource-based** — attached to the resource (S3 bucket policy, SQS queue policy, Lambda resource policy). Allow cross-account access.
- **Service Control Policies (SCPs)** — AWS Organizations layer, limits what accounts can do even with Allow.
- **Permission boundaries** — cap what an identity-based policy can grant.
- **Session policies** — passed at `AssumeRole` time, further restricts the session.

## IAM Roles — The Right Way to Grant Access

A **role** is an identity with a trust policy that says who can assume it, plus permission policies that say what it can do.

```json
// Trust policy — allows EC2 service to assume this role
{
  "Principal": { "Service": "ec2.amazonaws.com" },
  "Action": "sts:AssumeRole",
  "Effect": "Allow"
}
```

**Common role use cases:**

- **EC2 instance profile** — let your app on EC2 call S3/DynamoDB without credentials in code.
- **Cross-account role** — `Account A` trusts `Account B`'s developers to assume a read-only role.
- **GitHub Actions / CI** — OIDC federation: the CI runner gets a short-lived credential by presenting a JWT, no long-lived keys.

```bash
# Assume a role from the CLI
aws sts assume-role \
  --role-arn arn:aws:iam::123456789:role/deploy-role \
  --role-session-name deploy-session
```

## Least-Privilege in Practice

Start restrictive and add permissions only when needed. Practical steps:

1. **Never use `*` actions or resources** in production policies unless you have a specific reason.
2. **Use IAM Access Analyzer** to discover what permissions are actually used — remove the rest.
3. **Enable CloudTrail** so you have a log of every API call to audit.
4. **Require MFA** for sensitive actions with a Condition:

```json
"Condition": {
  "BoolIfExists": { "aws:MultiFactorAuthPresent": "true" }
}
```

5. **Rotate credentials** — even better, eliminate long-lived keys entirely by switching to roles + SSO.

## Permission Boundary Example

A boundary caps what a role can grant to others. Useful when you let a team manage their own IAM but don't want them to escalate privileges:

```json
// Even if the identity policy says Allow s3:*, the boundary limits it
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::team-bucket/*"
}
```

The effective permission is the **intersection** of the identity policy and the boundary.

## IAM Best Practices Summary

| Practice                            | Why                                   |
|-------------------------------------|---------------------------------------|
| Lock root account, enable MFA       | Root can do anything; protect it      |
| Use roles, not access keys          | Keys can leak; roles expire            |
| Use groups for humans               | Manage permissions at group level     |
| Enable IAM Access Analyzer          | Detect over-permissive policies       |
| Tag IAM resources                   | Audit, cost attribution               |
| Enable CloudTrail in all regions    | Full audit trail                      |
