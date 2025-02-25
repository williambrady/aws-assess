'''
This module is used to validate the AWS Organizations settings for the account.
modules/aws/organizations.py
'''
import boto3
import botocore.exceptions

def validate_organizations(profile, region):
    '''
    Validate the AWS Organizations settings for the account.

    Args:
        profile (str): AWS profile name
        region (str): AWS region

    Returns:
        None
    '''
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("organizations")

    try:
        # Check if part of an Org
        org_info = client.describe_organization()
        org_id = org_info['Organization']['Id']
        management_account = org_info['Organization'].get('MasterAccountId', 'Unknown')

        print(f"✔ Organization ID: {org_id}")
        print(f"✔ Management Account ID: {management_account}")

        # Check Active Org Members
        accounts = client.list_accounts()
        print("✔ Active Member Accounts:")
        for account in accounts["Accounts"]:
            if account["Status"] == "ACTIVE":
                print(f"  - {account['Id']}: {account['Name']}")

        # Delegated Admin settings
        admin_accounts = client.list_delegated_administrators()
        if admin_accounts.get("DelegatedAdministrators"):
            print("✔ Delegated Admins:")
            for admin in admin_accounts.get("DelegatedAdministrators", []):
                print(f"  - {admin['Id']}: {admin['Email']}")
        else:
            print("⚠ No Delegated Admins found.")

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error: {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
