# S3 Storage Classes and Cost Exercise

S3 offers multiple storage classes, each tuned for a different access pattern and price point. Choosing the right class is one of the simplest ways to cut an AWS bill.

## The Four Core Classes

| Class          | Use Case                              | Durability  | Price/GB/month |
|----------------|---------------------------------------|-------------|----------------|
| STANDARD       | Frequently accessed data              | 11 nines    | $0.023         |
| STANDARD_IA    | Infrequently accessed, rapid retrieval | 11 nines   | $0.0125        |
| GLACIER        | Archives, retrieved in minutes        | 11 nines    | $0.004         |
| DEEP_ARCHIVE   | Long-term archives, retrieved in hours | 11 nines   | $0.00099       |

"11 nines" durability (99.999999999%) means S3 is designed so that losing any given object is extraordinarily unlikely. It is a statistical design target — it does **not** protect against accidental deletion or overwrites. Enable **versioning** and optionally **replication** for that protection.

## Lifecycle Policies

Rather than manually moving objects, use an **S3 Lifecycle Policy** to automate transitions:

```json
{
  "Rules": [
    {
      "ID": "archive-old-logs",
      "Status": "Enabled",
      "Filter": { "Prefix": "logs/" },
      "Transitions": [
        { "Days": 30,  "StorageClass": "STANDARD_IA" },
        { "Days": 90,  "StorageClass": "GLACIER" },
        { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
      ],
      "Expiration": { "Days": 2555 }
    }
  ]
}
```

Objects in `logs/` automatically move through tiers and expire after 7 years.

## Cost Traps to Know

- **STANDARD_IA and GLACIER have minimum storage durations** — you pay for at least 30 days (IA) or 90 days (Glacier) even if you delete earlier.
- **Retrieval fees** — GLACIER and DEEP_ARCHIVE charge per-GB retrieval fees on top of storage. STANDARD has none.
- **Minimum object size** — STANDARD_IA charges a minimum of 128 KB per object. Storing millions of tiny files in IA is counter-productive.
- **Data transfer OUT is not free** — moving data to the internet costs $0.09/GB (first 10 TB, varies by region). VPC endpoints and CloudFront can reduce this.

## Intelligent-Tiering

If your access patterns are unknown or variable, **S3 Intelligent-Tiering** automatically moves objects between Frequent and Infrequent tiers based on access patterns, with no retrieval fees and no minimum object size penalty (for objects ≥ 128 KB).

## Exercise

In this exercise you will implement a simple S3 cost calculator. Given a list of objects with their current storage classes, compute the total monthly storage bill.

This reflects real work: teams audit their S3 buckets periodically and run cost simulations before changing lifecycle policies.

## Further Reading

- [S3 Storage Classes overview](https://aws.amazon.com/s3/storage-classes/)
- [NIST SP 800-145](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-145.pdf) — The NIST cloud computing definition covers the "measured service" characteristic, which is why cloud billing is per-unit-consumed — exactly what this exercise models.
