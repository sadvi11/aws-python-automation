# AWS Python Automation Suite

> Production-grade AWS operations automation using Python and Boto3 — EC2 control, S3 management, Lambda scheduling, CloudWatch monitoring, and SNS alerting.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-Boto3-FF9900?logo=amazonaws)](https://aws.amazon.com)
[![CloudWatch](https://img.shields.io/badge/CloudWatch-Monitoring-FF4F8B)]()
[![Lambda](https://img.shields.io/badge/Lambda-Serverless-FF9900?logo=awslambda)]()
[![Status](https://img.shields.io/badge/Status-Deployed%20%26%20Verified-2ea44f)]()

---

## What This Project Does

A Python Boto3 automation suite that replaces manual AWS console operations with
code-driven workflows. Covers the five most common cloud operations tasks: EC2
instance lifecycle management, S3 file operations, Lambda function scheduling,
CloudWatch alarm creation, and SNS email alerting. Each module is independently
usable and production-ready.

---

## Architecture

```
         ┌─────────────────────────────────────────┐
         │           main.py (Orchestrator)         │
         └──┬──────────┬──────────┬────────────┬────┘
            │          │          │            │
   ┌────────▼──┐ ┌─────▼──────┐ ┌▼─────────┐ ┌▼──────────────┐
   │ec2_       │ │s3_         │ │lambda_   │ │cloudwatch_    │
   │controller │ │uploader    │ │scheduler │ │alerts         │
   │           │ │            │ │          │ │               │
   │Start/Stop │ │Upload/List │ │Schedule  │ │Create Alarms  │
   │EC2        │ │S3 Objects  │ │Lambda    │ │CPU/Cost/Error │
   │Instances  │ │            │ │Invocations│ │+ SNS Email   │
   └─────┬─────┘ └─────┬──────┘ └────┬─────┘ └───────┬───────┘
         │             │             │               │
         └─────────────┴─────────────┴───────────────┘
                                 │
                        AWS Cloud (Boto3 SDK)
```

---

## Modules

| Module | AWS Service | What It Does |
|---|---|---|
| `ec2_controller.py` | EC2 | Start, stop, list instances by tag or region |
| `s3_uploader.py` | S3 | Upload files, list bucket contents, generate presigned URLs |
| `lambda_scheduler.py` | Lambda + EventBridge | Schedule Lambda functions, manage invocation rules |
| `cloudwatch_alerts.py` | CloudWatch + SNS | Create CPU, cost, and error rate alarms with email alerts |
| `main.py` | Orchestrator | Runs all modules in sequence with configurable parameters |

---

## Nokia OAM → AWS Operations Mapping

This toolkit applies Nokia OAM (Operations, Administration, Maintenance)
principles directly to cloud operations — the same operational discipline
used to manage 5G network infrastructure, applied to AWS resource management.

| Nokia OAM Function | AWS Automation Equivalent |
|---|---|
| Node health monitoring | CloudWatch alarms + SNS alerts |
| Resource provisioning | EC2 controller (start/stop/list) |
| Data collection | S3 uploader (logs, reports, configs) |
| Event scheduling | Lambda scheduler + EventBridge |
| Fault management | CloudWatch error rate alarms |

---

## Security Design

- **IAM least privilege** — Boto3 uses AWS credentials with minimum required permissions
- **No hardcoded credentials** — all credentials loaded from environment variables or AWS CLI config
- **SNS topic scoping** — alerts sent only to verified email endpoints
- **S3 presigned URLs** — time-limited access to objects, no permanent public exposure

---

## Key Design Decisions

**Why five separate modules instead of one script?**
Each module has a single responsibility — the same principle Nokia uses for
network function separation. `ec2_controller.py` only manages EC2. If EC2
logic changes, only one file changes. This is maintainable, testable, production-grade code.

**Why CloudWatch alarms instead of manual checking?**
Manual console monitoring does not scale. CloudWatch alarms with SNS notifications
mean issues are detected and reported automatically — the same proactive fault
detection Nokia OAM applies to 5G network nodes.

**Why Lambda scheduling over cron jobs?**
Lambda + EventBridge is serverless, managed, and requires zero server maintenance.
Cost is near-zero for scheduled tasks. No EC2 instance running 24/7 just to run a cron job.

---

## Quick Start

```bash
# Clone
git clone https://github.com/sadvi11/aws-python-automation.git
cd aws-python-automation

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Run all modules
python main.py

# Or run individual modules
python ec2_controller.py
python s3_uploader.py
python cloudwatch_alerts.py
python lambda_scheduler.py
```

---

## Example Output

```
EC2 Controller:
  ✓ Instance i-0abc123 → running
  ✓ Instance i-0def456 → stopped

S3 Uploader:
  ✓ Uploaded: report.csv → s3://my-bucket/reports/
  ✓ Generated presigned URL (valid 1 hour)

CloudWatch Alerts:
  ✓ CPU alarm created: threshold 80%
  ✓ SNS notification: sadhvisharma763@gmail.com

Lambda Scheduler:
  ✓ Rule created: daily-cleanup → 0 2 * * ? *
```

---

## Repository Structure

```
aws-python-automation/
├── main.py                 # Orchestrator — runs all modules
├── ec2_controller.py       # EC2 start/stop/list automation
├── s3_uploader.py          # S3 file operations and presigned URLs
├── lambda_scheduler.py     # Lambda scheduling with EventBridge
├── cloudwatch_alerts.py    # CloudWatch alarms + SNS email alerts
├── requirements.txt        # boto3, python-dotenv
├── .gitignore
└── README.md
```

---

## Interview Talking Points

- **Boto3 vs AWS CLI** — when to use each, why Python automation beats manual console work
- **IAM least privilege** — what permissions each module needs and why
- **CloudWatch alarms** — threshold types, alarm states, SNS integration
- **EventBridge vs CloudWatch Events** — the evolution and when each applies
- **S3 presigned URLs** — how they work, expiry, use cases
- **Lambda invocation types** — synchronous vs asynchronous vs event-driven

---

## Author

**Sadhvi Sharma** — Cloud & AI Engineer
Nokia India (5G Packet Core) → Cloud & AI Engineering
Calgary, AB, Canada | Permanent Resident | Open to Relocation

[LinkedIn](https://linkedin.com/in/sadhvi-sharma-5789a6249) | [GitHub](https://github.com/sadvi11)
