'''
This is the main file for the AWS Assessment CLI. It is responsible for parsing the command line arguments
and calling the appropriate functions to perform the assessment.
aws_assessment.py
'''
import argparse
import boto3
from modules.config import config
from modules.aws.account import validate_account, get_support_plan, get_billed_services, get_linked_accounts, get_regional_spend, get_account_id
from modules.aws.iam import validate_iam
from modules.aws.inspector import validate_inspector
from modules.aws.organizations import validate_organizations, get_member_accounts, get_organization_info
from modules.aws.controltower import validate_control_tower
from modules.aws.config import validate_aws_config
from modules.aws.securityhub import validate_security_hub

def run_assessment(session, profile, region, is_management, include_org_checks=True, include_control_tower=False):
    '''
    Runs the AWS assessment for a given profile.

    Args:
        session (boto3.Session): Boto3 session object
        profile (str): AWS profile name
        region (str): AWS region
        is_management (bool): True if the account is the management account, False otherwise.
        include_org_checks (bool): True to include AWS Organizations checks, False otherwise.
        include_control_tower (bool): True to include AWS Control Tower checks, False otherwise.

    Returns:
        None
    '''
    aws_account_id = get_account_id(session)
    print(f"\n🔍 Running assessment for profile: {profile}, {aws_account_id}, {region} \n")
    validate_account(session)
    print("\n🔍 AWS Support Plan Settings...")
    get_support_plan(session)
    print("\n🔍 Billed Services...")
    get_billed_services(session)
    print("\n🔍 Regional Spend...")
    get_regional_spend(session)
    print("\n🔍 Checking Accounts Relationships...")
    get_linked_accounts(session)
    print("\n🔍 Validating IAM Settings...")
    validate_iam(session)
    print("\n🔍 Validating AWS Config...")
    validate_aws_config(session, is_management)
    print("\n🔍 Validating AWS Security Hub...")
    validate_security_hub(session)
    print("\n🔍 Validating AWS Inspector...")
    validate_inspector(session)

    if include_org_checks:
        print("\n🔍 Validating AWS Organizations...")
        validate_organizations(session, profile)

    if include_control_tower:
        print("\n🔍 Validating AWS Control Tower...")
        validate_control_tower(session)

def main():
    '''
    Main function for the AWS Assessment CLI. It is responsible for parsing the command line arguments
    and calling the appropriate functions to perform the assessment.
    '''
    parser = argparse.ArgumentParser(description="AWS Security Assessment Tool")
    parser.add_argument("--simple", action="store_true", help="Perform the first phase of validation")
    parser.add_argument("--follow", action="store_true", help="Perform validation across all member accounts if initial account is management")
    args = parser.parse_args()

    # Load config
    profile = config.get("aws.profile")
    region = config.get("aws.region")

    # Setup boto session for initial connection
    global_session = boto3.Session(profile_name=profile, region_name=region)

    if args.simple or args.follow:
        # Determine if this is an Organization Management account
        # Determine if this is the management account
        org_id, management_account = get_organization_info(global_session)
        is_management = profile == management_account
        run_assessment(global_session, profile, region, is_management, include_org_checks=True, include_control_tower=True)

        if args.follow and is_management:
            print(f"\n🔍 Management account detected for Org {org_id}. Following into member accounts...\n")
            # get account list
            accounts = get_member_accounts(global_session)
            for account in accounts:
                specific_session = boto3.Session(profile_name=account, region_name=region)
                run_assessment(specific_session, account, region, is_management=False, include_org_checks=False, include_control_tower=False)

    print("\n✅ Assessment completed.")

if __name__ == "__main__":
    main()
