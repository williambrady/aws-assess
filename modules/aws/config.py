'''
This module is responsible for validating AWS Config settings.
modules/aws/config.py
'''
import boto3
import botocore.exceptions

def validate_aws_config(profile, region, is_management_account=True):
    '''
    Validate AWS Config settings.

    Args:
        profile (str): AWS profile name
        region (str): AWS region
        is_management_account (bool): Whether the account is the management account.
    '''
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("config")

    try:
        # Check if AWS Config is enabled
        recorders = client.describe_configuration_recorders()
        if not recorders.get("ConfigurationRecorders"):
            print("⚠ AWS Config is NOT Enabled")
        else:
            print("✔ AWS Config is Enabled")

        # Only check for an aggregator in the management account
        if is_management_account:
            aggregators = client.describe_configuration_aggregators()
            org_aggregators = [
                agg for agg in aggregators.get("ConfigurationAggregators", [])
                if agg.get("OrganizationAggregationSource") and agg["OrganizationAggregationSource"].get("AllAwsRegions", False)
            ]

            if org_aggregators:
                aggregator_name = org_aggregators[0].get("ConfigurationAggregatorName", "Unknown")
                print(f"✔ AWS Config Aggregator Found: {aggregator_name} (Organization-level)")
            else:
                print("⚠ No AWS Config Aggregator found with organization-level aggregation")

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Config): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
