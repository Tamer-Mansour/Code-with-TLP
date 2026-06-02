# Fargate and ECS - Running Containers on AWS

**Amazon ECS** (Elastic Container Service) is AWS's native container orchestrator. **AWS Fargate** is a serverless compute engine for containers — ECS manages scheduling, Fargate provides the infrastructure so you don't touch servers.

## Key concepts

| Concept         | Meaning                                                     |
|-----------------|-------------------------------------------------------------|
| **Cluster**     | Logical grouping of tasks/services; backed by EC2 or Fargate |
| **Task definition** | Blueprint: container image, CPU/memory, env vars, ports |
| **Task**        | A running instance of a task definition                     |
| **Service**     | Keeps N tasks running, integrates with a load balancer      |
| **Container registry** | ECR stores your Docker images                      |

## Deploying a container with Fargate

```bash
# 1. Push your image to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker build -t my-app .
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# 2. Create and run a task (minimal, IaC preferred in real projects)
aws ecs run-task \
  --cluster my-cluster \
  --launch-type FARGATE \
  --task-definition my-app:3 \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"
```

## Task definition snippet

```json
{
  "family": "my-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "portMappings": [{ "containerPort": 8080 }],
      "environment": [
        { "name": "ENV", "value": "production" }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Key points above:
- `secrets` pulls from Secrets Manager at runtime — the value never lands in your code or env vars at rest.
- `awslogs` log driver sends stdout/stderr to CloudWatch Logs automatically.
- `awsvpc` network mode gives each task its own ENI and security group.

## ECS Service with ALB

For a web service, create an **Application Load Balancer (ALB)** and attach it to the ECS service:

```
Internet → ALB (port 443) → Target group → ECS tasks (port 8080)
```

ECS registers/deregisters tasks from the target group automatically on deploy or scale events.

## Fargate vs EC2 launch type

| Concern               | Fargate                     | ECS on EC2             |
|-----------------------|-----------------------------|------------------------|
| Server management     | None                        | You manage instances   |
| Startup time          | ~30–60 s (cold)             | Fast (instance is ready)|
| Cost at scale         | Higher per vCPU/GB          | Cheaper with Spot      |
| GPU workloads         | Not supported               | Supported              |
| Windows containers    | Yes (limited)               | Yes (full)             |

Choose **Fargate** when you want minimal ops overhead. Choose **ECS on EC2** when you need Spot for cost savings, GPU, or extreme density.

## Auto Scaling

ECS services integrate with **Application Auto Scaling**:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/my-cluster/my-app \
  --min-capacity 2 --max-capacity 20

# Scale on CPU utilization
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    '{"TargetValue":60.0,"PredefinedMetricSpecification":{"PredefinedMetricType":"ECSServiceAverageCPUUtilization"}}'
```

## When to use what

```
Short burst tasks           → Lambda
Web APIs, microservices     → Fargate
Cost-sensitive batch        → ECS on EC2 Spot
Full orchestration / GitOps → EKS (Kubernetes)
```
