import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("MAXIO_ENDPOINT", "http://localhost:9000")
access_key = os.getenv("MAXIO_ACCESS_KEY", "minioadmin")
secret_key = os.getenv("MAXIO_SECRET_KEY", "minioadmin")
bucket = os.getenv("MAXIO_BUCKET", "pharma-prescriber")

client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

existing = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
if bucket not in existing:
    client.create_bucket(Bucket=bucket)
    print(f"Bucket created: {bucket}")
else:
    print(f"Bucket already exists: {bucket}")
