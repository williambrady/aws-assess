'''
AWS Organizations Validation
modules/aws/organizations.py
'''
import botocore.exceptions

def get_organization_info(session):
    '''
    Retrieve organization details and determine if this is the management account.
    '''
    client = session.client("organizations")

    try:
        org_info = client.describe_organization()
        org_id = org_info['Organization']['Id']
        management_account = org_info['Organization'].get('MasterAccountId', 'Unknown')

        return org_id, management_account
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("⚠ Skipping organization checks. This is a member account.")
        else:
            print(f"❌ AWS API Client error (Organizations): {e.response['Error']['Message']}")
        return None, None
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return None, None
    finally:
        session = None

def validate_organizations(session, profile):
    '''
    Validate AWS Organizations settings.
    '''
    org_id, management_account = get_organization_info(session)

    if not org_id:
        return False  # Skip checks if organization info couldn't be retrieved

    print(f"✔ Organization ID: {org_id}")
    print(f"✔ Management Account ID: {management_account}")

    is_management = profile == management_account

    if is_management:
        validate_member_accounts(session)
        validate_delegated_admins(session)

    return is_management

def validate_member_accounts(session):
    '''
    Retrieve and print active AWS member accounts.
    '''
    client = session.client("organizations")

    try:
        accounts = client.list_accounts()
        active_accounts = [account for account in accounts.get("Accounts", []) if account["Status"] == "ACTIVE"]

        if active_accounts:
            print("✔ Active Member Accounts:")
            for account in active_accounts:
                print(f"  - {account.get('Id', 'Unknown')}: {account.get('Name', 'Unknown')}")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Organizations - validate_member_accounts): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
    finally:
        session = None

def validate_delegated_admins(session):
    '''
    Retrieve and print delegated administrator accounts.
    '''
    client = session.client("organizations")

    try:
        delegated_admins = client.list_delegated_administrators()
        if delegated_admins.get("DelegatedAdministrators"):
            print("✔ Delegated Admin:")
            for admin in delegated_admins["DelegatedAdministrators"]:
                account_id = admin.get("Id", "Unknown")
                name = admin.get("Name", "Unknown")
                print(f"  - {account_id}: {name}")
        else:
            print("✔ No Delegated Admins Configured")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Organizations - validate_delegated_admins): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
    finally:
        session = None

def get_member_accounts(session):
    '''
    Retrieve a list of active AWS member account IDs with pagination.
    '''
    client = session.client("organizations")
    active_accounts = []

    try:
        paginator = client.get_paginator("list_accounts")
        for page in paginator.paginate():
            active_accounts.extend(
                [account["Id"] for account in page.get("Accounts", []) if account["Status"] == "ACTIVE"]
            )
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Organizations - get_member_accounts): {e.response['Error']['Message']}")
        return []
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
        return []

    return active_accounts
