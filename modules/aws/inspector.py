'''
This module is responsible for validating AWS Inspector settings.
modules/aws/inspector.py
'''
import botocore.exceptions

def validate_inspector(session):
    '''
    Validate AWS Inspector configuration.
    '''
    client = session.client("inspector2")

    try:
        org_config = client.describe_organization_configuration()
        auto_enable = org_config.get("autoEnable", {})

        print("✔ AWS Inspector is Enabled")
        print("✔ Inspector Account Management Settings:")
        print(f"  - Automatically activate for new member accounts: {all(auto_enable.values())}")
        print(f"  - Amazon EC2 scanning Enabled: {auto_enable.get('ec2', False)}")
        print(f"  - Amazon ECR scanning Enabled: {auto_enable.get('ecr', False)}")
        print(f"  - AWS Lambda standard scanning: {auto_enable.get('lambda', False)}")
        print(f"  - AWS Lambda code scanning: {auto_enable.get('lambdaCode', False)}")

    except botocore.exceptions.ClientError:
        print("⚠ Unable to retrieve organization configuration. Not a delegated admin? Falling back to standalone check...")
        run_standalone_inspector_check(session)
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error (Inspector): {str(e)}")

def run_standalone_inspector_check(session):
    '''
    Fallback for accounts that are not delegated admin. Checks local Inspector config.
    '''
    client = session.client("inspector2")

    try:
        config_response = client.get_configuration()
        ec2_configured = config_response.get("ec2Configuration", {}).get("scanModeState", {}).get("scanMode") is not None
        ecr_configured = config_response.get("ecrConfiguration", {}).get("rescanDurationState", {}).get("rescanDuration") is not None

        print("✔ AWS Inspector is Enabled")

        lambda_standard = False
        lambda_code = False

        try:
            response = client.list_coverage(
                filterCriteria={
                    "resourceType": [{"comparison": "EQUALS", "value": "AWS_LAMBDA_FUNCTION"}]
                },
                maxResults=100
            )

            for resource in response.get("coveredResources", []):
                scan_type = resource.get("scanType")
                if scan_type == "PACKAGE":
                    lambda_standard = True
                elif scan_type == "CODE":
                    lambda_code = True
        except botocore.exceptions.BotoCoreError as e:
            print(f"⚠ BotoCore error while checking Lambda coverage: {str(e)}")

        print("✔ Inspector Scan Configuration:")
        print(f"  - Amazon EC2 scanning Enabled: {ec2_configured}")
        print(f"  - Amazon ECR scanning Enabled: {ecr_configured}")
        print(f"  - AWS Lambda standard scanning: {lambda_standard}")
        print(f"  - AWS Lambda code scanning: {lambda_code if lambda_code else '⚠ Not reported'}")

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Inspector): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error (Inspector fallback): {str(e)}")
