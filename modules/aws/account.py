'''
This module is responsible for validating the AWS account. It checks if the billing and contact information is available.
modules/aws/account.py
'''
import boto3
import botocore.exceptions

def validate_account(profile, region):
    '''
    Validate the AWS account by checking if the billing and contact information is available.

    Args:
        profile (str): AWS profile name
        region (str): AWS region

    Returns:
        None
    '''
    session = boto3.Session(profile_name=profile, region_name=region)
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
