# Quiz: AWS Security and Observability

Test your understanding of IAM, Secrets Manager, KMS, CloudWatch, and related security concepts.

**Q1. What is the default behavior when an IAM policy has no explicit Allow or Deny for an action?**
- [ ] Allow, if the user is authenticated
- [ ] Allow, for users in the Admin group
- [x] Implicit Deny — access is blocked
- [ ] Depends on the resource type

**Q2. You want your EC2 instance to call S3 without embedding credentials in code. What is the correct approach?**
- [ ] Store an IAM access key in an environment variable on the instance
- [ ] Hard-code the access key in the application config file
- [x] Attach an IAM instance profile (role) to the EC2 instance
- [ ] Pass credentials via the EC2 user data script

**Q3. You have a Lambda that needs a database password. Where should it be stored and retrieved from?**
- [ ] Lambda environment variable (plaintext)
- [ ] Committed in a config file in the deployment package
- [x] AWS Secrets Manager, fetched at runtime and cached in a module-level variable
- [ ] Passed as a parameter in the Lambda event payload

**Q4. What does KMS envelope encryption do?**
- [ ] Encrypts data directly with the CMK for any size payload
- [x] Generates a data key, encrypts data locally with it, then stores the encrypted data key alongside the ciphertext
- [ ] Encrypts data using the public half of an RSA key
- [ ] Is only used for encrypting S3 bucket names

**Q5. Which CloudWatch feature lets you search and filter log data with a SQL-like query language?**
- [ ] CloudWatch Metrics
- [ ] CloudWatch Dashboards
- [x] CloudWatch Logs Insights
- [ ] CloudWatch Alarms

**Q6. A CloudWatch alarm is in the ALARM state. What does that mean?**
- [ ] AWS has detected a security threat
- [ ] The resource is offline
- [x] The monitored metric has crossed the configured threshold for the required evaluation periods
- [ ] The metric has no data points (INSUFFICIENT_DATA)

**Q7. What is a Dead-Letter Queue (DLQ) in SQS used for?**
- [ ] Storing messages that haven't been sent yet
- [x] Receiving messages that fail processing after a maximum number of retries
- [ ] Archiving all processed messages for auditing
- [ ] Routing messages to multiple consumers simultaneously

**Q8. You need to send one event to three different downstream services simultaneously. Which pattern fits best?**
- [ ] One SQS queue shared by all three services
- [ ] Three separate SQS FIFO queues with one producer each
- [x] SNS topic with three SQS queue subscriptions (fan-out)
- [ ] Lambda that calls each service sequentially

**Q9. An SQS message's visibility timeout expires before your Lambda finishes processing it. What happens?**
- [ ] The message is permanently deleted
- [ ] The message is moved to the DLQ
- [x] The message becomes visible again and another consumer may pick it up
- [ ] Processing continues uninterrupted; timeout only applies to idle messages

**Q10. Which of the following is a best practice for IAM?**
- [ ] Use the root account with MFA for daily administrative work
- [ ] Create a single IAM user shared across your team
- [x] Use IAM roles with least-privilege policies; avoid long-lived access keys
- [ ] Grant `*` actions and restrict access via resource tags
