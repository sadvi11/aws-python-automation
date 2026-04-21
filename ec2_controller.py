import boto3
import json
from datetime import datetime

# ================================
# EC2 Controller
# Author: Sadhvi - Cloud Engineer
# ================================

REGION = 'ca-central-1'

def get_all_instances():
    ec2 = boto3.client('ec2', region_name=REGION)
    response = ec2.describe_instances()
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'id': instance['InstanceId'],
                'state': instance['State']['Name'],
                'type': instance['InstanceType']
            })
    return instances

def start_instance(instance_id):
    ec2 = boto3.client('ec2', region_name=REGION)
    print(f"Starting instance: {instance_id}")
    ec2.start_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is starting...")

def stop_instance(instance_id):
    ec2 = boto3.client('ec2', region_name=REGION)
    print(f"Stopping instance: {instance_id}")
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} is stopping...")

def check_and_control():
    print("AWS EC2 Controller Starting...")
    print(f"Time: {datetime.now()}")
    
    instances = get_all_instances()
    
    if not instances:
        print("No EC2 instances found in ca-central-1")
        return
    
    print(f"\nFound {len(instances)} instances:")
    for instance in instances:
        print(f"  ID: {instance['id']} | State: {instance['state']} | Type: {instance['type']}")
    
    # Save report
    report = {
        'generated_at': str(datetime.now()),
        'total_instances': len(instances),
        'instances': instances
    }
    
    with open('ec2_report.json', 'w') as f:
        json.dump(report, f, indent=4)
    
    print("\nReport saved to ec2_report.json")

check_and_control()