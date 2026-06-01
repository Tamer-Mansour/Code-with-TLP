# Quiz: AWS Basics

**Q1. Which is the recommended way for humans to access AWS?**
- [ ] IAM user with long-lived access keys
- [x] IAM Identity Center (SSO) with role assumption
- [ ] Root account with MFA
- [ ] Direct console URL bookmark

**Q2. An Availability Zone is:**
- [ ] A geographic region (US, EU, etc.)
- [x] An isolated data center within a region
- [ ] A VPC subnet
- [ ] A subset of S3

**Q3. To grant an EC2 instance permission to read S3, you attach:**
- [ ] An access key to the instance
- [x] An IAM role via instance profile
- [ ] An S3 secret to the OS
- [ ] A bucket policy with the EC2 ID

**Q4. The unit of billing isolation is:**
- [ ] A VPC
- [ ] A region
- [x] An AWS account
- [ ] An IAM user

**Q5. Modern CI/CD pipelines should authenticate to AWS via:**
- [ ] Static access keys in secrets
- [x] OIDC federation (assume role via short-lived token)
- [ ] Root credentials
- [ ] An EC2 instance role on the runner

**Q6. The "infrastructure as code" tool maintained by HashiCorp is:**
- [ ] CloudFormation
- [ ] CDK
- [x] Terraform
- [ ] Pulumi
