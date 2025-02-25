'''
This module is responsible for validating IAM settings in the AWS account.
modules/aws/iam.py
'''
import boto3
import botocore.exceptions

def check_password_policy(client):
    '''
    Checks the IAM password policy and prints results.
    '''
    try:
        password_policy = client.get_account_password_policy()
        policy = password_policy.get("PasswordPolicy", {})

        min_length = policy.get("MinimumPasswordLength", 0)
        print(f"{'✔' if min_length >= 16 else '⚠'} Minimum Password Length: {min_length}")

        print(f"{'  ✔' if policy.get('RequireUppercaseCharacters', False) else '  ⚠'} Require Uppercase: {policy.get('RequireUppercaseCharacters', False)}")
        print(f"{'  ✔' if policy.get('RequireLowercaseCharacters', False) else '  ⚠'} Require Lowercase: {policy.get('RequireLowercaseCharacters', False)}")
        print(f"{'  ✔' if policy.get('RequireNumbers', False) else '  ⚠'} Require Numbers: {policy.get('RequireNumbers', False)}")
        print(f"{'  ✔' if policy.get('RequireSymbols', False) else '  ⚠'} Require Symbols: {policy.get('RequireSymbols', False)}")

        if "MaxPasswordAge" in policy:
            expire_days = policy.get("MaxPasswordAge", 0)
            if expire_days > 90:
                print(f"⚠ Password Expiration: {expire_days} days (Should be 90 or less)")
            elif expire_days == 90:
                print(f"✔ Password Expiration: {expire_days} days")
            else:
                print(f"👀 Password Expiration: {expire_days} days (Should be 90)")
        else:
            print("⚠ Password Expiration is not enforced!")

        reuse_prevention = policy.get("PasswordReusePrevention", 0)
        print(f"{'✔' if reuse_prevention >= 24 else '⚠'} Password Reuse Prevention: {reuse_prevention} passwords")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Password Policy): {e.response['Error']['Message']}")

def check_iam_users(client):
    '''
    Checks IAM users and their security settings.
    '''
    try:
        users = client.list_users()
        user_count = len(users.get('Users', []))
        print(f"{'⚠' if user_count > 0 else '✔'} IAM Users Found: {user_count}")

        if user_count == 0:
            return

        users_without_mfa = sum(1 for user in users.get('Users', []) if not client.list_mfa_devices(UserName=user['UserName']).get("MFADevices"))
        users_old_keys = sum(1 for user in users.get('Users', []) for key in client.list_access_keys(UserName=user['UserName']).get("AccessKeyMetadata", []) if (key.get("CreateDate").replace(tzinfo=None) - user.get("PasswordLastUsed", key.get("CreateDate")).replace(tzinfo=None)).days > 90)
        inactive_users = sum(1 for user in users.get('Users', []) if 'PasswordLastUsed' in user and (user['PasswordLastUsed'].replace(tzinfo=None) - user['CreateDate'].replace(tzinfo=None)).days > 30)
        never_logged_in = sum(1 for user in users.get('Users', []) if 'PasswordLastUsed' not in user)

        print(f"⚠ Users without MFA: {users_without_mfa}")
        print(f"{'⚠' if users_old_keys > 0 else '✔'} Users with Access Keys older than 90 days: {users_old_keys}")
        print(f"{'⚠' if inactive_users > 0 else '✔'} Users inactive for 30+ days: {inactive_users}")
        print(f"⚠ Users who never logged in: {never_logged_in}")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (IAM Users): {e.response['Error']['Message']}")

def validate_iam(profile, region):
    '''
    Validate the IAM settings in the AWS account.
    '''
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("iam")

    check_password_policy(client)
    check_iam_users(client)
