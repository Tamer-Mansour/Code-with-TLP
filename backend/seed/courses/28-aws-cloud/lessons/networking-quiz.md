# Quiz: VPC and Networking

Test your knowledge of VPC, subnets, security groups, and networking fundamentals on AWS.

**Q1. What makes a subnet "public" in a VPC?**
- [ ] It has a security group with inbound port 80 open
- [x] Its route table has a route `0.0.0.0/0` pointing to an Internet Gateway
- [ ] It has a public IP address range
- [ ] AWS assigns the label "public" when you create it

**Q2. You have an EC2 instance in a private subnet that needs to download packages from the internet. What do you add?**
- [ ] An Internet Gateway with a route from the private subnet
- [x] A NAT Gateway in a public subnet, with a route from the private subnet to the NAT Gateway
- [ ] An Elastic IP attached to the EC2 instance
- [ ] A VPC Peering connection to another VPC

**Q3. Security groups vs Network ACLs (NACLs) — which statement is correct?**
- [ ] Security groups are stateless; NACLs are stateful
- [x] Security groups are stateful; NACLs are stateless
- [ ] Both are stateless
- [ ] Both are stateful

**Q4. You want your Lambda function to call DynamoDB without traffic leaving AWS's network. What should you add?**
- [ ] A NAT Gateway
- [ ] An Elastic IP for the Lambda function
- [x] A VPC Endpoint for DynamoDB
- [ ] A Direct Connect connection

**Q5. Two VPCs need to communicate privately. VPC A is `10.0.0.0/16` and VPC B is `10.1.0.0/16`. What is the simplest solution?**
- [x] VPC Peering between the two VPCs
- [ ] A NAT Gateway in each VPC
- [ ] Transit Gateway (required even for two VPCs)
- [ ] PrivateLink

**Q6. What is the primary reason NAT Gateways can become expensive?**
- [ ] Per-hour charge at Reserved pricing
- [ ] They require a large EC2 instance underneath
- [x] Per-GB data processing fee on all traffic passing through them
- [ ] They require Elastic IPs which are billed hourly

**Q7. Which CIDR block gives you the most IP addresses in a VPC?**
- [ ] `10.0.0.0/24`
- [ ] `10.0.0.0/20`
- [x] `10.0.0.0/16`
- [ ] `10.0.0.0/28`

**Q8. You want to connect your on-premises data center to AWS with a dedicated private connection (not over the public internet). Which service do you use?**
- [ ] Site-to-Site VPN
- [x] AWS Direct Connect
- [ ] VPC Peering
- [ ] Transit Gateway
