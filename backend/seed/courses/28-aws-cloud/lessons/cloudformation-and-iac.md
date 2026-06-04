# CloudFormation and Infrastructure as Code

The AWS Well-Architected Framework's Operational Excellence pillar starts here: **if your infrastructure is not in code, it does not exist**. CloudFormation is AWS's native IaC tool — a YAML or JSON template that becomes a running stack of AWS resources.

## A Minimal Template

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: S3 bucket with versioning enabled

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "my-data-${AWS::AccountId}"
      VersioningConfiguration:
        Status: Enabled

Outputs:
  BucketName:
    Value: !Ref DataBucket
```

`!Sub`, `!Ref`, and `!GetAtt` are **intrinsic functions** — CloudFormation's built-in substitution language for wiring resources together without hardcoding ARNs.

## Stacks and Change Sets

A **stack** is one deployed instance of a template. To update safely:

1. Create a **Change Set** — a preview of what will be added, modified, or deleted.
2. Review the changes.
3. Execute the Change Set.

Never apply a template update directly in production without reviewing the change set first. A single property change on an RDS instance can trigger a replacement (new DB, data migration required).

## Intrinsic Functions Quick Reference

| Function       | What It Does                                      |
|----------------|---------------------------------------------------|
| `!Ref`         | Returns the resource's primary identifier         |
| `!GetAtt`      | Returns a resource attribute (e.g., ARN, DNS)     |
| `!Sub`         | String substitution with `${Variable}` syntax     |
| `!If`          | Conditional resource creation                     |
| `!ImportValue` | Cross-stack reference via `Outputs`               |

## AWS CDK: IaC in Real Code

CDK (Cloud Development Kit) lets you write infrastructure in Python, TypeScript, Java, or Go. The CDK synthesizes CloudFormation templates — so it's CloudFormation under the hood, but with the full power of a programming language.

```python
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
)
from constructs import Construct

class AppStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(self, "DataBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        fn = _lambda.Function(self, "Processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda"),
        )
        bucket.grant_read(fn)
```

CDK constructs handle boilerplate (like IAM roles and event notifications) that you would write manually in raw CloudFormation.

## Drift Detection

After deployment, humans sometimes make manual changes in the console. CloudFormation **Drift Detection** compares the actual resource state to the template and flags discrepancies.

```bash
aws cloudformation detect-stack-drift --stack-name my-stack
```

Running drift detection weekly (or on a schedule via EventBridge) is a good practice to catch configuration drift before it causes an outage.

## Common Pitfalls

- **No deletion policy on databases** — by default, CloudFormation deletes an RDS instance when the stack is deleted. Add `DeletionPolicy: Retain` to stateful resources.
- **Hard-coded account IDs and region names** — use `AWS::AccountId` and `AWS::Region` pseudo-parameters.
- **Circular dependencies** — two resources that each reference the other. Use `DependsOn` carefully or break into nested stacks.
- **Too-large templates** — CloudFormation has a 1 MB template size limit. Use nested stacks or CDK's implicit template splitting.

## Further Reading

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) — The Operational Excellence pillar mandates IaC as a foundational practice.
- [Cloud Computing Open Course (CS 7125)](https://alg.manifoldapp.org/projects/cs7125-ksu) — Covers IaC and AWS infrastructure patterns with open lecture materials.
