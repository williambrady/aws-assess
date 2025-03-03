'''
This module is responsible for validating the AWS account. It checks if the billing and contact information is available.
modules/aws/account.py
'''
import datetime
import botocore.exceptions

def validate_account(session):
    '''
    Validate the AWS account by checking if the billing and contact information is available.

    Args:
        profile (str): AWS profile name
        region (str): AWS region

    Returns:
        None
    '''
    client = session.client("account")

    try:
        # Account Contact Information
        account_info = client.get_contact_information()
        if "ContactInformation" in account_info:
            contact = account_info["ContactInformation"]
            print(f"✔ Account Contact Found - Full Name: {contact.get('FullName', 'N/A')}")
            print(f"  Company: {contact.get('CompanyName', 'N/A')}")
            print(f"  Address: {contact.get('AddressLine1', 'N/A')} {contact.get('AddressLine2', '')}, {contact.get('City', 'N/A')}, {contact.get('StateOrRegion', 'N/A')}, {contact.get('CountryCode', 'N/A')}, {contact.get('PostalCode', 'N/A')}")
            print(f"  Phone: {contact.get('PhoneNumber', 'N/A')}")
        else:
            print("❌ Account Contact Information not found.")

        # Fetch Alternate Contact Types
        contact_types = ["BILLING", "OPERATIONS", "SECURITY"]
        for contact_type in contact_types:
            try:
                contact_info = client.get_alternate_contact(AlternateContactType=contact_type)
                print(f"✔ {contact_type} Contact Found: {contact_info['AlternateContact']['EmailAddress']}")
            except client.exceptions.ResourceNotFoundException:
                print(f"⚠ No {contact_type} contact configured.")

    except botocore.exceptions.NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your credentials.")
    except botocore.exceptions.PartialCredentialsError:
        print("❌ AWS credentials are incomplete. Check your credentials file.")
    except botocore.exceptions.EndpointConnectionError:
        print("❌ Unable to connect to AWS. Check your network.")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error: {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")

def get_support_plan(session):
    '''
    Retrieve the AWS Support Plan attached to the account.
    AWS does not have a direct API to get this, so we infer it by checking if the Support API is accessible.

    Args:
        session (boto3.Session): Boto3 session object

    Returns:
        str: The support plan name (Basic, Developer, Business, Enterprise) or Unknown if not found.
    '''
    client = session.client("support", region_name="us-east-1")  # AWS Support is a global service

    try:
        # Try listing support cases to infer the support plan
        client.describe_cases(maxResults=10)
        print("✔ AWS Support Plan: Business, Enterprise, or Developer")
        return "Business, Enterprise, or Developer"
    except botocore.exceptions.ClientError as e:
        error_message = e.response["Error"]["Message"]
        # pylint: disable=R1705
        if "SubscriptionRequiredException" in str(error_message):
            print("✔ AWS Support Plan: Basic (Free Tier)")
            return "Basic (Free Tier)"
        else:
            print(f"❌ AWS API Client error (Support Plan): {error_message}")
            return "Unknown"
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return "Unknown"

def get_billed_services(session):
    '''
    Retrieve a summary of all AWS services that have generated cost greater than $0.00 in the last 45 days.
    Returns a list of services that have incurred charges.

    Args:
        session (boto3.Session): Boto3 session object

    Returns:
        list: A list of AWS services that have incurred charges in the last 45 days.
    '''
    client = session.client("ce", region_name="us-east-1")
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                "Start": (datetime.datetime.utcnow() - datetime.timedelta(days=45)).strftime("%Y-%m-%d"),
                "End": datetime.datetime.utcnow().strftime("%Y-%m-%d")
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )

        services = [
            entry["Keys"][0] for entry in response.get("ResultsByTime", [])[0].get("Groups", [])
            if float(entry["Metrics"]["UnblendedCost"]["Amount"]) > 0.00
        ]

        if services:
            print("✔ Billed AWS Services in the Last 45 Days:")
            for service in sorted(services):
                print(f"  - {service}")
        else:
            print("✔ No AWS services have generated costs in the last 45 days.")
        return services

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Billed Services): {e.response['Error']['Message']}")
        return []
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return []

def get_linked_accounts(session):
    '''
    Retrieve a list of accounts linked to the current account as the master payer.
    If the account is outside the organization, denote it with a warning.

    Args:
        session (boto3.Session): Boto3 session object

    Returns:
        list: A list of linked AWS account IDs and names.
    '''
    client = session.client("organizations")
    try:
        response = client.list_accounts()
        linked_accounts = [
            f"  - {account['Id']}: {account['Name']}"
            for account in response.get("Accounts", [])
        ]

        if linked_accounts:
            print("✔ Linked AWS Accounts:")
            for account in linked_accounts:
                print(account)
        else:
            print("⚠ No linked accounts found or account is outside an AWS Organization.")
        return linked_accounts

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Linked Accounts): {e.response['Error']['Message']}")
        return []
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return []

def get_regional_spend(session):
    '''
    Retrieve a summary of AWS spend by region for the last 45 days.
    Services without a region will be grouped under "Global".
    '''
    client = session.client("ce", region_name="us-east-1")
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                "Start": (datetime.datetime.utcnow() - datetime.timedelta(days=45)).strftime("%Y-%m-%d"),
                "End": datetime.datetime.utcnow().strftime("%Y-%m-%d")
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}]
        )

        regions = {
            entry["Keys"][0] if entry["Keys"][0] else "Global": float(entry["Metrics"]["UnblendedCost"]["Amount"])
            for entry in response.get("ResultsByTime", [])[0].get("Groups", [])
            if float(entry["Metrics"]["UnblendedCost"]["Amount"]) > 0.00
        }

        if regions:
            print("✔ Regional AWS Spend in the Last 45 Days:")
            for region, cost in sorted(regions.items()):
                print(f"  - {region}: ${cost:.2f}")
        else:
            print("✔ No AWS spend recorded in the last 45 days.")
        return regions

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Regional Spend): {e.response['Error']['Message']}")
        return {}
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return {}
