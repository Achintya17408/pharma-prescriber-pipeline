import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:7410',
    aws_access_key_id='maxio',
    aws_secret_access_key='maxio123',
    config=Config(signature_version="s3v4"),
    region_name='us-east-1'
)

bucket = 'pharma-raw'
existing = [b['Name'] for b in s3.list_buckets()['Buckets']]
if bucket not in existing:
    s3.create_bucket(Bucket=bucket)
    print("Bucket 'pharma-raw' created successfully")
else:
    print("Bucket 'pharma-raw' already exists")
print("Existing buckets:", [b['Name'] for b in s3.list_buckets()['Buckets']])
