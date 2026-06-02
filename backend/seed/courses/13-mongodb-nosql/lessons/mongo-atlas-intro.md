# MongoDB Atlas — Managed Cloud Deployment

**MongoDB Atlas** is the fully managed cloud database service from MongoDB, Inc. It removes the operational burden of provisioning servers, upgrading MongoDB versions, configuring replica sets, and managing backups.

## Key Features

| Feature | Description |
|---|---|
| **Managed replica sets** | Atlas automatically provisions a 3-node replica set; failover is handled for you |
| **Atlas Search** | Lucene-powered full-text search directly on your MongoDB data, no separate Elasticsearch cluster |
| **Atlas Vector Search** | Store and query vector embeddings for AI/ML applications |
| **Online Archive** | Automatically move cold data to cheap object storage while keeping it queryable |
| **Atlas Data API** | REST/GraphQL API over your collections, no driver needed |
| **Charts** | Built-in data visualization connected directly to your collections |
| **Triggers** | Serverless functions that fire on change stream events or on a schedule |

## Free Tier (M0)

Atlas offers a **free shared cluster (M0)** with:
- 512 MB storage
- Shared vCPU and RAM
- Available on AWS, GCP, and Azure
- No credit card required

M0 is ideal for learning, prototypes, and side projects. For production use, start with an M10 or higher dedicated cluster.

## Connecting from Your Application

After creating a cluster, Atlas gives you a connection string:

```
mongodb+srv://username:password@cluster0.abcde.mongodb.net/mydb?retryWrites=true&w=majority
```

```python
# Python (pymongo)
from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://user:pass@cluster0.abcde.mongodb.net/mydb",
    serverSelectionTimeoutMS=5000
)
db = client.mydb
print(db.list_collection_names())
```

```javascript
// Node.js (mongodb driver)
const { MongoClient } = require("mongodb");
const client = new MongoClient(process.env.MONGODB_URI);

async function main() {
  await client.connect();
  const db = client.db("mydb");
  console.log(await db.listCollections().toArray());
}
main().finally(() => client.close());
```

## IP Access List and Network Security

Atlas blocks all inbound connections by default. You must add your IP (or `0.0.0.0/0` for development) to the **Network Access** allowlist, and create a **Database User** with a password.

For production:
- Use VPC peering or Private Link instead of public internet access.
- Restrict database users to the minimum required roles (`readWrite` on specific DBs, not `Atlas admin`).

## Atlas CLI

You can manage clusters, users, and backups from the command line:

```bash
# Install
brew install mongodb-atlas-cli

# Login
atlas auth login

# Create a free cluster
atlas clusters create myCluster --provider AWS --region US_EAST_1 --tier M0

# Get the connection string
atlas clusters connectionStrings describe myCluster
```

## Monitoring and Alerts

Atlas provides built-in monitoring dashboards (operations/second, latency percentiles, replication lag) and lets you set alerts on metrics like query execution time, disk IOPS, or replica lag. Alerts can notify via email, Slack, PagerDuty, or a webhook.

Atlas is the recommended way to run MongoDB for teams that want to focus on application development rather than database operations.
