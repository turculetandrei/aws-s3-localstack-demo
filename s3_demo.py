"""S3 demo on LocalStack using boto3: bucket and object lifecycle."""

import hashlib
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

ENDPOINT_URL = "http://localhost:4566"
BUCKET = "capi-demo-bucket-py"
KEY = "notite.txt"

BASE_DIR = Path(__file__).resolve().parent
ORIGINAL = BASE_DIR / "notite.txt"
DOWNLOADED = BASE_DIR / "notite_descarcat_py.txt"


def sha256_of(path):
    """Return the SHA256 hash of a file (uppercase, like PowerShell)."""
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    # S3 client pointed at LocalStack
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )

    print(f"\n[1/8] Create bucket: {BUCKET}")
    s3.create_bucket(Bucket=BUCKET)
    print("Bucket created.")

    print(f"\n[2/8] Upload notite.txt to s3://{BUCKET}/{KEY}")
    s3.upload_file(str(ORIGINAL), BUCKET, KEY)
    print("Upload done.")

    print(f"\n[3/8] List objects in s3://{BUCKET}")
    response = s3.list_objects_v2(Bucket=BUCKET)
    for obj in response.get("Contents", []):
        print(f"{obj['Key']}  {obj['Size']} bytes")

    print(f"\n[4/8] Download s3://{BUCKET}/{KEY} to {DOWNLOADED.name}")
    s3.download_file(BUCKET, KEY, str(DOWNLOADED))
    print("Download done.")

    print("\n[5/8] Compare SHA256 of original vs downloaded")
    hash_original = sha256_of(ORIGINAL)
    hash_downloaded = sha256_of(DOWNLOADED)
    print(f"Original:   {hash_original}")
    print(f"Downloaded: {hash_downloaded}")
    if hash_original == hash_downloaded:
        print("MATCH")
    else:
        print("MISMATCH")
        sys.exit(1)

    print(f"\n[6/8] Delete object s3://{BUCKET}/{KEY}")
    s3.delete_object(Bucket=BUCKET, Key=KEY)
    print("Object deleted.")

    print(f"\n[7/8] Delete bucket: {BUCKET}")
    s3.delete_bucket(Bucket=BUCKET)
    print("Bucket deleted.")

    print("\n[8/8] List buckets (should be empty)")
    names = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    print(names)
    if BUCKET not in names:
        print(f"Confirmed: {BUCKET} is gone.")


if __name__ == "__main__":
    try:
        main()
    except (ClientError, BotoCoreError, OSError) as err:
        print(f"\nERROR: {err}", file=sys.stderr)
        sys.exit(1)
    print("\nDemo finished successfully.")
