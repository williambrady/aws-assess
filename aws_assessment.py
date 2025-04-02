'''
This is the main file for the AWS Assessment CLI. It is responsible for parsing the command line arguments
and calling the appropriate functions to perform the assessment.
aws_assessment.py
'''
import argparse
from dataclasses import dataclass
import boto3
from modules.config import config
from modules.aws.account import validate_account, get_support_plan, get_billed_services, get_linked_accounts, get_regional_spend, get_account_id
from modules.aws.iam import validate_iam
from modules.aws.inspector import validate_inspector
from modules.aws.organizations import validate_organizations, get_member_accounts, get_organization_info
from modules.aws.controltower import validate_control_tower
from modules.aws.config import validate_aws_config
from modules.aws.securityhub import validate_security_hub
from modules.aws.guardduty import validate_guardduty

@dataclass
class AssessmentOptions:
    '''
    Data class to hold assessment options.
    '''
    session: boto3.Session
    profile: str
    region: str
    is_management: bool
    include_org_checks: bool = True
    include_control_tower: bool = False

def run_assessment(options: AssessmentOptions):
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
    aws_account_id = get_account_id(options.session)
    print(f"\n🔍 Running assessment for profile: {options.profile}, {aws_account_id}, {options.region} \n")
    validate_account(options.session)
    print("\n🔍 AWS Support Plan Settings...")
    get_support_plan(options.session)
    print("\n🔍 Billed Services...")
    get_billed_services(options.session)
    print("\n🔍 Regional Spend...")
    get_regional_spend(options.session)
    print("\n🔍 Checking Accounts Relationships...")
    get_linked_accounts(options.session)
    print("\n🔍 Validating IAM Settings...")
    validate_iam(options.session)
    print("\n🔍 Validating AWS Config...")
    validate_aws_config(options.session, options.is_management)
    print("\n🔍 Validating AWS Security Hub...")
    validate_security_hub(options.session)
    print("\n🔍 Validating AWS Inspector...")
    validate_inspector(options.session)
    print("\n🔍 Validating AWS GuardDuty...")
    validate_guardduty(options.session)

    if options.include_org_checks:
        print("\n🔍 Validating AWS Organizations...")
        validate_organizations(options.session, options.profile)

    if options.include_control_tower:
        print("\n🔍 Validating AWS Control Tower...")
        validate_control_tower(options.session)

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

        options = AssessmentOptions(
            session=global_session,
            profile=profile,
            region=region,
            is_management=is_management,
            include_org_checks=True,
            include_control_tower=True
        )
        run_assessment(options)

        if args.follow and is_management:
            print(f"\n🔍 Management account detected for Org {org_id}. Following into member accounts...\n")
            # get account list
            accounts = get_member_accounts(global_session)
            for account in accounts:
                specific_session = boto3.Session(profile_name=account, region_name=region)
                options = AssessmentOptions(
                    session=specific_session,
                    profile=account,
                    region=region,
                    is_management=False,
                    include_org_checks=True,
                    include_control_tower=False
                )
                run_assessment(options)

    print("\n✅ Assessment completed.")

if __name__ == "__main__":
    main()
