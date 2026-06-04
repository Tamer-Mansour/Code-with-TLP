# EC2 Auto Scaling Exercise

Auto Scaling Groups (ASGs) are the backbone of elastic, self-healing applications on AWS. Instead of provisioning for peak, you let the ASG add and remove capacity automatically based on demand.

## How Target Tracking Works

Target tracking is the simplest and most common scaling policy. You declare a target metric value — for example, "keep average CPU at 60%" — and AWS adjusts the instance count to maintain it.

Under the hood, the scaling algorithm works like this:

```
desired = ceil(current_capacity × (metric_value / target_value))
```

AWS also builds in a **scale-in cooldown** (scale-in only fires when the metric drops far enough below target, by default when it falls below 90% of the target). This prevents thrashing when the metric hovers near the target.

## Launch Templates and Instance Refresh

An ASG uses a **Launch Template** to define the EC2 configuration for new instances — AMI ID, instance type, security groups, IAM role, user-data script. When you update the template (e.g., to deploy a new AMI), you trigger an **Instance Refresh** to gradually replace existing instances.

```
old instances ──► drain, terminate (one at a time or in batches)
new instances ──► launch from updated template
```

## Scaling Policy Types

| Type              | Best for                                       |
|-------------------|------------------------------------------------|
| Target Tracking   | Most workloads — just set the target           |
| Step Scaling      | Custom multi-tier responses to alarm thresholds|
| Scheduled Scaling | Predictable load patterns (business hours)     |
| Predictive Scaling | ML-based forecasting of future demand         |

## Lifecycle Hooks

Lifecycle hooks let you pause an instance during launch or termination to run custom logic:

- **Launch hook** — wait for a configuration management tool to finish before the instance goes in-service.
- **Termination hook** — drain connections or ship logs before the instance is killed.

```
PENDING → (hook fires) → PENDING:WAIT → PENDING:PROCEED → IN_SERVICE
```

## Common Pitfalls

- **Too-narrow launch template**: If you specify only one instance type and it's unavailable in an AZ, the ASG can't scale. Use a mixed-instances policy with multiple types.
- **Scaling on a lagging metric**: CPU is reported every 60 seconds. Use detailed monitoring (10-second metrics) for faster responses.
- **Not testing scale-in**: Always verify that your application handles instance termination gracefully (draining, no session stickiness without ELB).

## Exercise

In this exercise you will simulate a single-metric target tracking policy. This mirrors the exact formula AWS uses, giving you intuition for why Auto Scaling sometimes over- or under-shoots your target.

## Further Reading

- [EC2 Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)
- [AWS Well-Architected Framework — Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html): The Reliability pillar's design principle "scale horizontally to increase aggregate workload availability" is directly enabled by Auto Scaling Groups.
