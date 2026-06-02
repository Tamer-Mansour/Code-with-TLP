# RDS and DynamoDB - Managed Databases on AWS

AWS offers both **relational** (RDS, Aurora) and **NoSQL** (DynamoDB) managed database services. Choosing the right one — and configuring it securely — is one of the most important architectural decisions you'll make.

## RDS — Relational Database Service

RDS manages PostgreSQL, MySQL, MariaDB, Oracle, and SQL Server. AWS handles backups, patching, replication, and failover. You still design the schema and write the queries.

### Creating an RDS instance

```bash
aws rds create-db-instance \
  --db-instance-identifier prod-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 16.2 \
  --master-username admin \
  --master-user-password "$(aws secretsmanager get-secret-value --secret-id db-master-pw --query SecretString --output text)" \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name prod-db-subnet-group \
  --multi-az \
  --backup-retention-period 7 \
  --no-publicly-accessible
```

Key flags:
- `--multi-az` — synchronous standby in a second AZ; automatic failover in ~1–2 min.
- `--no-publicly-accessible` — the DB is in a private subnet, reachable only from within the VPC.
- `--backup-retention-period 7` — daily automated snapshots kept for 7 days.

### Aurora

Aurora is AWS's cloud-native relational engine, compatible with MySQL and PostgreSQL but significantly faster (up to 5x MySQL, 3x PostgreSQL). Key differences:

| Feature            | RDS                         | Aurora                         |
|--------------------|-----------------------------|--------------------------------|
| Storage            | Per-instance, resizes manually | Auto-grows to 128 TB         |
| Read replicas      | Up to 5, async              | Up to 15, near-zero lag        |
| Failover time      | ~1–2 min                    | ~30 s (writer failover)        |
| Serverless option  | No                          | Aurora Serverless v2           |
| Price              | Lower upfront               | 20% higher per ACU             |

For new projects: prefer **Aurora PostgreSQL** unless you have a strong reason for standard RDS.

### RDS Proxy

A connection pooler managed by AWS. Sits between your app and RDS:

```
Lambda (many short-lived connections) → RDS Proxy → RDS
```

Crucial for **Lambda + RDS** — Lambdas can open thousands of concurrent connections; RDS Proxy queues and multiplexes them so the DB doesn't run out of connections.

## DynamoDB — Managed NoSQL

DynamoDB is a serverless key-value and document store. Single-digit millisecond reads at any scale. No schema migrations, no connection pooling.

### Data model

- **Table** — the top-level resource.
- **Item** — a row. Every item must have a partition key (`pk`), optionally a sort key (`sk`).
- **Attributes** — any additional fields; types are flexible per item.

```python
import boto3

table = boto3.resource("dynamodb").Table("orders")

# Write
table.put_item(Item={
    "pk": "user#42",
    "sk": "order#2024-11-01T10:00:00Z",
    "total": 49.99,
    "status": "shipped"
})

# Read
response = table.get_item(Key={"pk": "user#42", "sk": "order#2024-11-01T10:00:00Z"})
print(response["Item"]["total"])  # 49.99

# Query all orders for a user
response = table.query(
    KeyConditionExpression="pk = :pk AND begins_with(sk, :prefix)",
    ExpressionAttributeValues={":pk": "user#42", ":prefix": "order#"}
)
```

### Capacity modes

| Mode           | When to use                            | Cost model                |
|----------------|----------------------------------------|---------------------------|
| On-Demand      | Unpredictable, spiky traffic           | Per request               |
| Provisioned    | Steady, predictable traffic            | Per RCU/WCU reserved      |
| Auto Scaling   | Provisioned with upper/lower bounds    | Provisioned + scaling fee |

**RCU** = 1 strongly consistent read of up to 4 KB.  
**WCU** = 1 write of up to 1 KB.

### Global tables

DynamoDB **Global Tables** replicate data across multiple AWS regions with ~1s lag. Each region can serve reads and writes. Use for global apps and disaster recovery.

### When to choose RDS vs DynamoDB

| Need                                    | Choose      |
|-----------------------------------------|-------------|
| Complex joins, transactions, ACID       | RDS/Aurora  |
| Known access patterns, massive scale    | DynamoDB    |
| Flexible schema, item-level differences | DynamoDB    |
| Reporting, analytics queries            | RDS         |
| Ultra-low latency key lookups           | DynamoDB    |
| Strong consistency across many tables   | RDS         |

## Security for databases

- Always place databases in **private subnets** — no public IP, no internet route.
- Use **IAM authentication** for RDS instead of static passwords where possible.
- Enable **encryption at rest** (default in modern RDS, mandatory for compliance workloads).
- Use **Secrets Manager** to store and rotate database credentials automatically.
- Restrict security groups: only allow inbound on port 5432/3306 from your app tier SG.
