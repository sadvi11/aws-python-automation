"""
api_gateway.py — API Gateway REST API Automation
────────────────────────────────────────────────────────────────
Creates a REST API on AWS API Gateway with Lambda integration:
  - POST /sentiment  → Lambda function (sentiment classifier)
  - GET  /health     → Lambda function (health check)
  - Deploys to 'dev' stage
  - Configures CORS headers
  - Adds IAM invoke permission for API Gateway → Lambda

Use case: Expose the canadian-financial-sentiment SageMaker
endpoint as a public REST API via API Gateway + Lambda.

Run: python api_gateway.py
"""

import boto3
import json
import logging
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "ca-central-1")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "")
API_NAME = "smartmoney-sentiment-api"
STAGE_NAME = "dev"

# Lambda function to integrate with (must exist)
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "smartmoney-sentiment-handler")


class APIGatewayManager:
    """Creates and manages REST APIs on AWS API Gateway."""

    def __init__(self):
        self.client = boto3.client("apigateway", region_name=AWS_REGION)
        self.lambda_client = boto3.client("lambda", region_name=AWS_REGION)
        self.api_id = None

    # ── API Lifecycle ─────────────────────────────────────────────────────────

    def create_api(self) -> str:
        """Create a REST API and return the API ID."""
        response = self.client.create_rest_api(
            name=API_NAME,
            description="SmartMoney Canada — Financial Sentiment REST API",
            endpointConfiguration={"types": ["REGIONAL"]},
            tags={
                "Project":     "SmartMoneyCanada",
                "Environment": "dev",
                "ManagedBy":   "aws-python-automation",
            },
        )
        self.api_id = response["id"]
        logger.info(f"API created: {API_NAME} (ID: {self.api_id})")
        return self.api_id

    def get_or_create_api(self) -> str:
        """Get existing API or create new one."""
        apis = self.client.get_rest_apis()
        for api in apis.get("items", []):
            if api["name"] == API_NAME:
                self.api_id = api["id"]
                logger.info(f"Found existing API: {self.api_id}")
                return self.api_id
        return self.create_api()

    def get_root_resource_id(self) -> str:
        """Get the root resource ID (/) for the API."""
        resources = self.client.get_resources(restApiId=self.api_id)
        for resource in resources["items"]:
            if resource["path"] == "/":
                return resource["id"]
        raise ValueError("Root resource not found")

    # ── Resource + Method Setup ───────────────────────────────────────────────

    def create_resource(self, parent_id: str, path_part: str) -> str:
        """Create a path resource (e.g. /sentiment, /health)."""
        try:
            response = self.client.create_resource(
                restApiId=self.api_id,
                parentId=parent_id,
                pathPart=path_part,
            )
            resource_id = response["id"]
            logger.info(f"Resource created: /{path_part} (ID: {resource_id})")
            return resource_id
        except ClientError as e:
            if "ConflictException" in str(e):
                # Resource already exists — find and return it
                resources = self.client.get_resources(restApiId=self.api_id)
                for r in resources["items"]:
                    if r.get("pathPart") == path_part:
                        return r["id"]
            raise

    def add_lambda_method(
        self,
        resource_id: str,
        http_method: str,
        lambda_arn: str,
    ) -> None:
        """
        Add HTTP method to resource with Lambda proxy integration.
        Lambda proxy passes full request to Lambda and returns its response.
        """
        # Create method (no auth for dev)
        try:
            self.client.put_method(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType="NONE",
                apiKeyRequired=False,
            )
            logger.info(f"Method added: {http_method}")
        except ClientError as e:
            if "ConflictException" not in str(e):
                raise

        # Lambda proxy integration URI
        integration_uri = (
            f"arn:aws:apigateway:{AWS_REGION}:lambda:path"
            f"/2015-03-31/functions/{lambda_arn}/invocations"
        )

        # Create Lambda proxy integration
        self.client.put_integration(
            restApiId=self.api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            type="AWS_PROXY",
            integrationHttpMethod="POST",  # Lambda invocations are always POST
            uri=integration_uri,
        )
        logger.info(f"Lambda integration set: {http_method} → {lambda_arn}")

        # Method response — 200 OK
        try:
            self.client.put_method_response(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode="200",
                responseModels={"application/json": "Empty"},
            )
        except ClientError:
            pass

    def add_cors(self, resource_id: str) -> None:
        """Add CORS OPTIONS method to resource."""
        try:
            self.client.put_method(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod="OPTIONS",
                authorizationType="NONE",
            )
            self.client.put_integration(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod="OPTIONS",
                type="MOCK",
                requestTemplates={"application/json": '{"statusCode": 200}'},
            )
            self.client.put_method_response(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod="OPTIONS",
                statusCode="200",
                responseParameters={
                    "method.response.header.Access-Control-Allow-Headers": False,
                    "method.response.header.Access-Control-Allow-Methods": False,
                    "method.response.header.Access-Control-Allow-Origin":  False,
                },
                responseModels={"application/json": "Empty"},
            )
            self.client.put_integration_response(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod="OPTIONS",
                statusCode="200",
                responseParameters={
                    "method.response.header.Access-Control-Allow-Headers":
                        "'Content-Type,Authorization'",
                    "method.response.header.Access-Control-Allow-Methods":
                        "'GET,POST,OPTIONS'",
                    "method.response.header.Access-Control-Allow-Origin":
                        "'*'",
                },
            )
            logger.info("CORS OPTIONS method added")
        except ClientError:
            logger.info("CORS already configured")

    # ── Lambda Permission ─────────────────────────────────────────────────────

    def grant_api_gateway_invoke(self, lambda_arn: str) -> None:
        """Allow API Gateway to invoke the Lambda function."""
        try:
            self.lambda_client.add_permission(
                FunctionName=lambda_arn,
                StatementId=f"apigateway-invoke-{self.api_id}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:aws:execute-api:{AWS_REGION}:{AWS_ACCOUNT_ID}:{self.api_id}/*/*",
            )
            logger.info("Lambda invoke permission granted to API Gateway")
        except ClientError as e:
            if "ResourceConflictException" in str(e):
                logger.info("Permission already exists")
            else:
                raise

    # ── Deploy ────────────────────────────────────────────────────────────────

    def deploy(self, stage: str = STAGE_NAME) -> str:
        """Deploy the API to a stage and return the invoke URL."""
        response = self.client.create_deployment(
            restApiId=self.api_id,
            stageName=stage,
            stageDescription=f"{stage} environment",
            description="Deployed by aws-python-automation",
        )
        deployment_id = response["id"]

        invoke_url = (
            f"https://{self.api_id}.execute-api.{AWS_REGION}.amazonaws.com/{stage}"
        )
        logger.info(f"Deployed to stage: {stage}")
        logger.info(f"Invoke URL: {invoke_url}")
        logger.info(f"POST {invoke_url}/sentiment")
        logger.info(f"GET  {invoke_url}/health")
        return invoke_url

    def delete_api(self) -> None:
        """Delete the REST API."""
        confirm = input(f"Delete API '{API_NAME}' ({self.api_id})? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Cancelled.")
            return
        self.client.delete_rest_api(restApiId=self.api_id)
        logger.info(f"API deleted: {self.api_id}")

    def list_apis(self) -> list:
        """List all REST APIs in the account."""
        apis = self.client.get_rest_apis()
        for api in apis.get("items", []):
            logger.info(f"  {api['id']} — {api['name']}")
        return apis.get("items", [])


def build_api(lambda_arn: str) -> str:
    """
    Full API Gateway setup:
    1. Create REST API
    2. Create /sentiment (POST) and /health (GET) resources
    3. Add Lambda proxy integration to both
    4. Add CORS
    5. Grant invoke permission
    6. Deploy to dev stage
    """
    gw = APIGatewayManager()

    print("=" * 50)
    print("API Gateway Setup — SmartMoney Canada")
    print(f"Region: {AWS_REGION}")
    print(f"Lambda: {lambda_arn}")
    print("=" * 50)

    # Create API
    print("\n1. Creating REST API...")
    gw.get_or_create_api()

    # Get root resource
    root_id = gw.get_root_resource_id()

    # Create /sentiment resource
    print("\n2. Creating /sentiment resource (POST)...")
    sentiment_id = gw.create_resource(root_id, "sentiment")
    gw.add_lambda_method(sentiment_id, "POST", lambda_arn)
    gw.add_cors(sentiment_id)

    # Create /health resource
    print("\n3. Creating /health resource (GET)...")
    health_id = gw.create_resource(root_id, "health")
    gw.add_lambda_method(health_id, "GET", lambda_arn)

    # Grant permissions
    print("\n4. Granting API Gateway → Lambda invoke permission...")
    gw.grant_api_gateway_invoke(lambda_arn)

    # Deploy
    print("\n5. Deploying to dev stage...")
    invoke_url = gw.deploy()

    print(f"\nAPI READY:")
    print(f"  POST {invoke_url}/sentiment")
    print(f"  GET  {invoke_url}/health")
    print(f"\nTo delete: python api_gateway.py --delete")
    return invoke_url


if __name__ == "__main__":
    import sys

    if "--list" in sys.argv:
        gw = APIGatewayManager()
        gw.list_apis()
    elif "--delete" in sys.argv:
        gw = APIGatewayManager()
        gw.get_or_create_api()
        gw.delete_api()
    else:
        # Build API — requires Lambda function ARN
        lambda_arn = os.getenv("LAMBDA_FUNCTION_ARN", "")
        if not lambda_arn:
            print("Set LAMBDA_FUNCTION_ARN in .env or environment")
            print("Example: arn:aws:lambda:ca-central-1:123456789:function:my-func")
            sys.exit(1)
        build_api(lambda_arn)
