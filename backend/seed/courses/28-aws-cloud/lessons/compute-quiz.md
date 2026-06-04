# Quiz: Compute and Storage

**Q1. Which EC2 pricing model gives up to 90% savings but can be interrupted with a 2-minute warning?**
- [ ] Reserved Instances
- [ ] On-Demand
- [x] Spot Instances
- [ ] Savings Plans

**Q2. What is the maximum execution timeout for an AWS Lambda function?**
- [ ] 5 minutes
- [ ] 10 minutes
- [x] 15 minutes
- [ ] 30 minutes

**Q3. Which EBS volume type is best for high-throughput sequential workloads like MapReduce?**
- [ ] gp3 (General Purpose SSD)
- [ ] io2 (Provisioned IOPS SSD)
- [x] st1 (Throughput Optimized HDD)
- [ ] sc1 (Cold HDD)

**Q4. Lambda "Provisioned Concurrency" is used to:**
- [ ] Reduce per-invocation billing costs
- [x] Eliminate cold starts by pre-initializing execution environments
- [ ] Increase the maximum memory allocation
- [ ] Allow Lambda to run longer than 15 minutes

**Q5. Which S3 storage class has a minimum billable storage duration of 90 days?**
- [ ] STANDARD_IA
- [ ] INTELLIGENT_TIERING
- [x] GLACIER
- [ ] STANDARD

**Q6. An Auto Scaling Group's "Launch Template" defines:**
- [ ] The scaling policy thresholds
- [ ] When to schedule scale-in events
- [x] The EC2 instance configuration for new instances (AMI, type, user data, IAM role)
- [ ] The Elastic Load Balancer target group

**Q7. S3's "11 nines" durability means:**
- [ ] 100% guarantee that no object will ever be lost
- [ ] S3 automatically backs up every object to a secondary region
- [x] It is a statistical design target — versioning is still needed to protect against accidental deletion
- [ ] Objects are replicated to at least 11 data centers

**Q8. Which invocation type allows a Lambda to process messages from an SQS queue?**
- [ ] Synchronous
- [ ] Asynchronous
- [x] Poll-based (event source mapping)
- [ ] Direct HTTP trigger
