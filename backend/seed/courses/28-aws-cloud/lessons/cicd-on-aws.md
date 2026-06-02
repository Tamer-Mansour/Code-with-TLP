# CI/CD on AWS - CodePipeline, CodeBuild, and GitHub Actions

A CI/CD pipeline automatically tests and deploys your code on every push. AWS offers native tools (CodePipeline, CodeBuild, CodeDeploy) and integrates tightly with GitHub Actions. This lesson covers both approaches.

## AWS Native CI/CD

### CodeBuild — build and test

CodeBuild runs your build in a managed Docker container. Define the build steps in a `buildspec.yml` at the root of your repo:

```yaml
# buildspec.yml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install -r requirements.txt

  pre_build:
    commands:
      - echo "Running tests..."
      - pytest tests/ -v

  build:
    commands:
      - echo "Building Docker image..."
      - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
      - docker build -t $IMAGE_URI .
      - docker push $IMAGE_URI

  post_build:
    commands:
      - printf '[{"name":"app","imageUri":"%s"}]' $IMAGE_URI > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```

### CodePipeline — orchestrate stages

A CodePipeline connects Source → Build → Deploy stages:

```
GitHub (source) → CodeBuild (test + build) → ECS (deploy)
```

```bash
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

CodePipeline supports approval gates (a human must click Approve before the production stage runs).

### CodeDeploy — deployment strategies

| Strategy        | Description                                    | Zero downtime |
|-----------------|------------------------------------------------|---------------|
| In-place        | Stop, deploy, start on same instances          | No            |
| Blue/Green      | New instances, switch traffic when healthy     | Yes           |
| Canary          | 10% traffic to new → wait → 100%               | Yes           |
| Linear          | 10% every N minutes until 100%                 | Yes           |

For Lambda, CodeDeploy shifts traffic between function versions:

```bash
aws deploy create-deployment \
  --application-name my-lambda-app \
  --deployment-group-name production \
  --deployment-config-name CodeDeployDefault.LambdaCanary10Percent5Minutes
```

## GitHub Actions + AWS

GitHub Actions is widely used with AWS via **OIDC federation** — no long-lived keys required.

### Setup OIDC trust (one-time)

```bash
# Create the OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --client-id-list sts.amazonaws.com

# Create a role that GitHub Actions can assume
# Trust policy allows only pushes from your repo on the main branch
```

```json
{
  "Principal": {
    "Federated": "arn:aws:iam::123456789:oidc-provider/token.actions.githubusercontent.com"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
    }
  }
}
```

### Workflow file

```yaml
# .github/workflows/deploy.yml
name: Deploy to ECS

on:
  push:
    branches: [main]

permissions:
  id-token: write   # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
          aws-region: us-east-1

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPO:$GITHUB_SHA .
          docker push $ECR_REGISTRY/$ECR_REPO:$GITHUB_SHA

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: task-definition.json
          service: my-service
          cluster: my-cluster
          wait-for-service-stability: true
```

## Comparing approaches

| Aspect                   | AWS Native (CodePipeline) | GitHub Actions       |
|--------------------------|--------------------------|----------------------|
| Setup effort             | Medium (AWS console/IaC) | Low (YAML in repo)   |
| Visibility               | AWS Console              | GitHub UI            |
| Ecosystem                | AWS-centric              | Huge marketplace     |
| Cost                     | CodeBuild minutes + Pipeline | GitHub Actions minutes |
| OIDC (no keys)           | Built-in                 | Configured manually  |

For AWS-heavy teams, CodePipeline is a natural fit. Most teams starting from scratch choose GitHub Actions for its rich ecosystem and familiar interface.

## Deployment best practices

- Run all tests before any deployment stage.
- Use Blue/Green or Canary for production — never in-place on production ECS/Lambda.
- Store image tags by commit SHA, not `latest` — `latest` is not reproducible.
- Gate production deployments with a manual approval step.
- Post deployment, run a smoke test (ping `/health`) before deleting the old version.
