import boto3
import json
import zipfile
import os
from datetime import datetime

# ================================
# Lambda Scheduler
# Author: Sadhvi - Cloud Engineer
# ================================

REGION = 'ca-central-1'
FUNCTION_NAME = 'sadhvi-scheduled-function'
ROLE_NAME = 'sadhvi-lambda-role'

def create_lambda_zip():
    # Create the Lambda function code
    lambda_code = '''
import json
from datetime import datetime

def lambda_handler(event, context):
    print(f"Lambda running at: {datetime.now()}")
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scheduled Lambda running!',
            'timestamp': str(datetime.now())
        })
    }
'''
    with open('/tmp/lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    with zipfile.ZipFile('/tmp/lambda.zip', 'w') as z:
        z.write('/tmp/lambda_function.py', 'lambda_function.py')
    
    print("Lambda zip created!")

def get_or_create_role():
    iam = boto3.client('iam')
    
    try:
        role = iam.get_role(RoleName=ROLE_NAME)
        print(f"Role exists: {ROLE_NAME}")
        return role['Role']['Arn']
    except:
        print(f"Creating role: {ROLE_NAME}")
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        import time
        time.sleep(10)
        print(f"Role created!")
        return role['Role']['Arn']

def create_lambda(role_arn):
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    with open('/tmp/lambda.zip', 'rb') as f:
        zip_content = f.read()
    
    try:
        response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Scheduled Lambda by Sadhvi',
            Timeout=30
        )
        print(f"Lambda created: {FUNCTION_NAME}")
        return response['FunctionArn']
    except Exception as e:
        if 'ResourceConflictException' in str(e):
            print(f"Lambda already exists!")
            response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
            return response['Configuration']['FunctionArn']
        else:
            print(f"Error: {e}")
            return None

def run():
    print("Lambda Scheduler Starting...")
    
    create_lambda_zip()
    role_arn = get_or_create_role()
    function_arn = create_lambda(role_arn)
    
    if function_arn:
        print(f"\nLambda Function ARN: {function_arn}")
        print("Lambda is ready to run on schedule!")
    
    print("\nLambda setup complete!")

run()