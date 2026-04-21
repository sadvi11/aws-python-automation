import boto3
import json
import os
from datetime import datetime

# ================================
# S3 File Uploader
# Author: Sadhvi - Cloud Engineer
# ================================

REGION = 'ca-central-1'
BUCKET_NAME = 'sadhvi-automation-bucket-2026'

def create_bucket():
    s3 = boto3.client('s3', region_name=REGION)
    try:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"Bucket {BUCKET_NAME} created!")
    except Exception as e:
        if 'BucketAlreadyOwnedByYou' in str(e):
            print(f"Bucket already exists — skipping!")
        else:
            print(f"Error: {e}")

def upload_file(filename):
    s3 = boto3.client('s3', region_name=REGION)
    print(f"Uploading {filename}...")
    s3.upload_file(filename, BUCKET_NAME, filename)
    print(f"Uploaded: {filename}")

def list_files():
    s3 = boto3.client('s3', region_name=REGION)
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    print(f"\nFiles in bucket:")
    for f in files:
        print(f"  - {f}")
    return files

def run():
    print("S3 File Uploader Starting...")
    
    create_bucket()
    
    # Create a sample file to upload
    with open('sample_data.txt', 'w') as f:
        f.write(f"AWS Automation Report\nGenerated: {datetime.now()}\nAuthor: Sadhvi - Cloud Engineer")
    
    upload_file('sample_data.txt')
    list_files()
    
    print("\nS3 upload complete!")

run()