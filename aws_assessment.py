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

def run_assessment(profile, region, include_org_checks=True):
    '''
    Runs the AWS assessment for a given profile.
    '''
    print(f"\n🔍 Running assessment for profile: {profile}\n")
    validate_account(profile, region)
    print("\n🔍 Validating IAM Settings...")
    validate_iam(profile, region)

    if include_org_checks:
        print("\n🔍 Validating AWS Organizations...")
        validate_organizations(profile, region)

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
        run_assessment(profile, region, include_org_checks=True)

        if args.follow:
            # Get the list of accounts in the organization
            session = boto3.Session(profile_name=profile, region_name=region)
            client = session.client("organizations")
            org_info = client.describe_organization()
            management_account = org_info['Organization'].get('MasterAccountId')

            if profile == management_account:
                print("\n🔍 Management account detected. Following into member accounts...\n")
                accounts = client.list_accounts()
                for account in accounts["Accounts"]:
                    if account["Status"] == "ACTIVE":
                        account_id = account["Id"]
                        run_assessment(account_id, region, include_org_checks=False)

        print("\n✅ Assessment completed.")

if __name__ == "__main__":
    main()
