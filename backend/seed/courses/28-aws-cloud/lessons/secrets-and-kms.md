# Secrets Manager and KMS - Managing Credentials and Encryption

Hard-coding credentials in source code is one of the most common causes of security incidents. AWS provides two managed services to keep secrets safe: **AWS Secrets Manager** for storing and rotating credentials, and **AWS KMS** (Key Management Service) for encryption key management.

## AWS Secrets Manager

Secrets Manager stores strings — database passwords, API keys, OAuth tokens — as versioned secrets. Access is controlled by IAM policies, and secrets can be automatically rotated.

### Storing and retrieving a secret

```bash
# Store a database password
aws secretsmanager create-secret \
  --name prod/postgres/master \
  --secret-string '{"username":"admin","password":"Str0ngP@ssw0rd!"}'

# Retrieve it in an app
aws secretsmanager get-secret-value \
  --secret-id prod/postgres/master \
  --query SecretString \
  --output text
```

In Python, with caching to avoid repeated API calls:

```python
import boto3
import json

_cache = {}

def get_secret(secret_name: str) -> dict:
    if secret_name not in _cache:
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        _cache[secret_name] = json.loads(response["SecretString"])
    return _cache[secret_name]

creds = get_secret("prod/postgres/master")
conn = psycopg2.connect(
    host=DB_HOST,
    user=creds["username"],
    password=creds["password"]
)
```

Cache at module level; Lambda reuses the execution environment for subsequent invocations, so repeated calls don't hit the API every time.

### Automatic rotation

Secrets Manager can rotate credentials on a schedule using a Lambda function. For supported databases (RDS MySQL, PostgreSQL, Oracle, SQL Server), AWS provides built-in rotation lambdas:

```bash
aws secretsmanager rotate-secret \
  --secret-id prod/postgres/master \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:xxx:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

After rotation, the old version stays available (tagged `AWSPREVIOUS`) until the next rotation, giving running apps time to pick up the new value.

## AWS KMS — Key Management Service

KMS manages cryptographic keys. You don't handle raw key material; you call KMS to encrypt and decrypt.

### Key types

| Type                    | Who controls key material | Use case                          |
|-------------------------|--------------------------|-----------------------------------|
| AWS-managed key         | AWS                      | Automatic encryption for S3, EBS  |
| Customer-managed key (CMK) | You                  | Custom rotation, audit, cross-account |
| AWS CloudHSM            | You (hardware)           | Compliance requiring hardware keys |

### Encrypting data with KMS

```python
import boto3, base64

kms = boto3.client("kms")
KEY_ID = "arn:aws:kms:us-east-1:xxx:key/yyy"

# Encrypt
response = kms.encrypt(
    KeyId=KEY_ID,
    Plaintext=b"sensitive value"
)
ciphertext = base64.b64encode(response["CiphertextBlob"]).decode()

# Decrypt (KMS knows the key from the ciphertext)
response = kms.decrypt(CiphertextBlob=base64.b64decode(ciphertext))
plaintext = response["Plaintext"].decode()
```

KMS limits: max 4 KB per encrypt call. For large data, use **envelope encryption**:

1. KMS generates a **data key** (plaintext + encrypted).
2. You encrypt your data locally with the plaintext key using AES-256.
3. Store the encrypted data + encrypted data key together.
4. To decrypt: call KMS to decrypt the data key, then decrypt your data locally.

### KMS integration with other services

KMS integrates natively with most AWS services:

```bash
# S3 bucket with KMS encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {
      "SSEAlgorithm": "aws:kms",
      "KMSMasterKeyID": "arn:aws:kms:us-east-1:xxx:key/yyy"
    }}]
  }'
```

## Secrets Manager vs Parameter Store

**AWS Systems Manager Parameter Store** is a simpler, cheaper alternative to Secrets Manager for non-secret config and low-frequency secrets:

| Feature                 | Secrets Manager | Parameter Store (Advanced) |
|-------------------------|-----------------|---------------------------|
| Automatic rotation      | Yes             | No (manual)               |
| Cross-account access    | Yes             | With IAM                  |
| Versioning              | Yes             | Yes                       |
| Cost                    | $0.40/secret/month | $0.05/param/month     |
| Best for                | DB credentials, API keys | Feature flags, config |

Rule of thumb: use **Secrets Manager** for anything that rotates or is highly sensitive; use **Parameter Store** for application configuration.

## Best practices summary

- Never store credentials in environment variables injected at deploy time from a CI pipeline.
- Always fetch from Secrets Manager at runtime; cache in memory.
- Grant the least-privilege IAM permission: `secretsmanager:GetSecretValue` on the specific ARN only.
- Enable **CloudTrail** for KMS API calls — every encrypt/decrypt is auditable.
- Rotate all credentials at least every 90 days; use Secrets Manager rotation for zero-downtime rotation.
