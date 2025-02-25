'''
This is the main file for the AWS Assessment CLI. It is responsible for parsing the command line arguments
and calling the appropriate functions to perform the assessment.
/aws_assessment.py
'''
import argparse
import boto3
from modules.config import config
from modules.aws.account import validate_account
from modules.aws.iam import validate_iam
from modules.aws.organizations import validate_organizations
from modules.aws.controltower import validate_control_tower
from modules.aws.config import validate_aws_config

def run_assessment(profile, region, is_management_account, include_org_checks=True, include_control_tower=False):
    '''
    Runs the AWS assessment for a given profile.
    '''
    print(f"\n🔍 Running assessment for profile: {profile}\n")
    validate_account(profile, region)
    print("\n🔍 Validating IAM Settings...")
    validate_iam(profile, region)
    print("\n🔍 Validating AWS Config...")
    validate_aws_config(profile, region, is_management_account)

    if include_org_checks:
        print("\n🔍 Validating AWS Organizations...")
        validate_organizations(profile, region)

    if include_control_tower:
        print("\n🔍 Validating AWS Control Tower...")
        validate_control_tower(profile, region)

def main():
    '''
    Main function for the AWS Assessment CLI. It is responsible for parsing the command line arguments
    and calling the appropriate functions to perform the assessment.
    '''
    parser = argparse.ArgumentParser(description="AWS Assessment CLI")
    parser.add_argument("--simple", action="store_true", help="Perform the first phase of validation")
    parser.add_argument("--follow", action="store_true", help="Perform validation across all member accounts if initial account is management")
    args = parser.parse_args()

    # Load config
    profile = config.get("aws.profile")
    region = config.get("aws.region")

    if args.simple or args.follow:
        print("Starting assessment...\n")
        session = boto3.Session(profile_name=profile, region_name=region)
        client = session.client("organizations")
        org_info = client.describe_organization()
        management_account = org_info['Organization'].get('MasterAccountId')

        is_management = profile == management_account
        run_assessment(profile, region, is_management, include_org_checks=True, include_control_tower=True)

        if args.follow and is_management:
            print("\n🔍 Management account detected. Following into member accounts...\n")
            accounts = client.list_accounts()
            for account in accounts["Accounts"]:
                if account["Status"] == "ACTIVE":
                    account_id = account["Id"]
                    run_assessment(account_id, region, is_management_account=False, include_org_checks=False, include_control_tower=False)

        print("\n✅ Assessment completed.")

if __name__ == "__main__":
    main()
