import boto3
import json
from datetime import datetime

# ================================
# CloudWatch Monitoring + SNS Alerts
# Author: Sadhvi - Cloud Engineer
# ================================

REGION = 'ca-central-1'
SNS_TOPIC_NAME = 'sadhvi-alerts'
EMAIL = 'sadhvisharma0705@gmail.com'  #  email

def create_sns_topic():
    sns = boto3.client('sns', region_name=REGION)
    
    print("Creating SNS topic...")
    response = sns.create_topic(Name=SNS_TOPIC_NAME)
    topic_arn = response['TopicArn']
    print(f"SNS Topic created: {topic_arn}")
    
    # Subscribe email
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=EMAIL
    )
    print(f"Subscription email sent to: {EMAIL}")
    print("Check your email and confirm the subscription!")
    
    return topic_arn

def create_cloudwatch_alarm(topic_arn):
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)
    
    print("\nCreating CloudWatch alarm...")
    
    cloudwatch.put_metric_alarm(
        AlarmName='sadhvi-high-cpu-alarm',
        AlarmDescription='Alert when CPU exceeds 80%',
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistic='Average',
        Period=300,
        EvaluationPeriods=1,
        Threshold=80.0,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[topic_arn],
        TreatMissingData='notBreaching'
    )
    
    print("CloudWatch alarm created!")
    print("You will get email alert when CPU goes above 80%")

def check_alarms():
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)
    
    response = cloudwatch.describe_alarms()
    alarms = response['MetricAlarms']
    
    print(f"\nActive CloudWatch Alarms:")
    for alarm in alarms:
        print(f"  - {alarm['AlarmName']} | State: {alarm['StateValue']}")
    
    return alarms

def run():
    print("CloudWatch Monitoring + SNS Alerts Starting...")
    
    topic_arn = create_sns_topic()
    create_cloudwatch_alarm(topic_arn)
    check_alarms()
    
    # Save report
    report = {
        'generated_at': str(datetime.now()),
        'sns_topic': SNS_TOPIC_NAME,
        'alarm': 'sadhvi-high-cpu-alarm',
        'threshold': '80% CPU',
        'email': EMAIL
    }
    
    with open('cloudwatch_report.json', 'w') as f:
        json.dump(report, f, indent=4)
    
    print("\nReport saved to cloudwatch_report.json")
    print("CloudWatch setup complete!")

run()