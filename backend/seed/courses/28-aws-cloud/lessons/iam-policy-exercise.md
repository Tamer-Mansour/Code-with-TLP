# IAM Policy Evaluation Exercise

Understanding how AWS evaluates IAM policies is essential for passing certification exams and for debugging real-world permission issues.

## IAM Policy Evaluation in a Nutshell

Every API call to AWS goes through the policy evaluation engine. The engine checks all applicable policies — identity-based policies, resource-based policies, Service Control Policies (SCPs), and permission boundaries — and produces a single verdict: **Allow** or **Deny**.

The rules are simple but absolute:

1. **Explicit Deny wins** — if any policy statement denies the action, the request is rejected immediately. No other Allow can override a Deny.
2. **Explicit Allow required** — if no Deny exists, there must be at least one Allow for the request to succeed.
3. **Default Deny** — if no statement matches at all, the answer is Deny (known as an "implicit deny").

## Why Explicit Deny Matters

Imagine you have a developer role with broad S3 access. Your security team wants to ensure nobody can ever delete objects in the production bucket — even if future policies grant it. The solution is an explicit Deny statement in an SCP or permission boundary:

```json
{
  "Effect": "Deny",
  "Action": "s3:DeleteObject",
  "Resource": "arn:aws:s3:::prod-data/*"
}
```

No matter what Allow policies are added later, this Deny cannot be overridden. It is the highest-priority outcome in IAM evaluation.

## Wildcard Actions

IAM action patterns support a single `*` wildcard, typically at the end:

```json
"Action": "s3:*"          // all S3 actions
"Action": "ec2:Describe*" // all Describe actions on EC2
"Action": "*"             // every action across all services (use with extreme caution)
```

A pattern like `s3:*` matches `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, and every other S3 action.

## Common Misconceptions

- **"An Allow in one policy overrides a Deny in another"** — FALSE. Explicit Deny always wins, regardless of source or order.
- **"If I don't Deny something, it's allowed"** — FALSE. The default is Deny. You need an explicit Allow.
- **"The last policy evaluated wins"** — FALSE. AWS evaluates all applicable policies simultaneously, and Deny takes precedence.

## Exercise

In this exercise you will implement the AWS policy evaluation algorithm. Given N policy statements and a target action, apply the rules above to output `ALLOW` or `DENY`.

This tests your understanding of the evaluation logic that underpins every AWS permission decision.

## Further Reading

- [AWS IAM Policy Evaluation Logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [NIST SP 800-146](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-146.pdf) — "Cloud Computing Synopsis and Recommendations" covers cloud security governance, which underpins why fine-grained access control models like IAM exist.
