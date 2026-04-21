# AWS Python Automation Suite

A complete Python + boto3 automation suite that controls AWS infrastructure — EC2, S3, Lambda, CloudWatch and SNS alerts.

## Tech Stack
- Python 3
- boto3 (AWS SDK)
- AWS EC2, S3, Lambda, CloudWatch, SNS
- ca-central-1 region

## What It Does

### 1. EC2 Controller
- Connects to AWS EC2
- Lists all instances with state and type
- Can start and stop instances automatically
- Saves JSON report

### 2. S3 File Uploader
- Creates S3 bucket automatically
- Uploads files to S3
- Lists all files in bucket

### 3. Lambda Scheduler
- Creates IAM role automatically
- Deploys Lambda function to AWS
- Function ready to run on schedule

### 4. CloudWatch Monitoring + SNS Alerts
- Creates SNS topic for alerts
- Subscribes email for notifications
- Creates CloudWatch alarm for CPU > 80%
- Sends email alert when threshold breached

## How to Run

1. Install dependencies:
pip install -r requirements.txt

2. Configure AWS:
aws configure

3. Run individual scripts:
python3 ec2_controller.py
python3 s3_uploader.py
python3 lambda_scheduler.py
python3 cloudwatch_alerts.py

4. Or run everything at once:
python3 main.py

## Sample Output
SNS Topic created: arn:aws:sns:ca-central-1:XXXX:sadhvi-alerts
Subscription email sent to: your-email@gmail.com
CloudWatch alarm created!
You will get email alert when CPU goes above 80%

## Why This Matters
Manual AWS management wastes hours every day.
This suite automates everything — start/stop servers, upload files, monitor costs, send alerts.
This is exactly how DevOps engineers manage AWS in Canadian companies.

## Author
Sadhvi - Cloud Engineer | AWS Certified Solution Architect