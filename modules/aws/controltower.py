'''
This module is responsible for validating AWS Control Tower settings in the management account.
modules/aws/controltower.py
'''
import botocore.exceptions

def check_controltower_service_enabled(session):
    '''
    Check if AWS Control Tower service is enabled by inspecting IAM roles and policies.
    Returns:
        tuple: (bool, str) where bool indicates if Control Tower is enabled,
               and str is the managing account ID if available.
    '''
    iam = session.client("iam")

    try:
        # Check if the AWSControlTowerExecution role exists
        iam.get_role(RoleName="AWSControlTowerExecution")
        print("✔ AWSControlTowerExecution role found.")

        # Check trust policy to find managing account
        trust_policy = iam.get_role(RoleName="AWSControlTowerExecution")["Role"]["AssumeRolePolicyDocument"]
        # print(f"DEBUG: Trust Policy: {trust_policy}")

        statements = trust_policy.get("Statement", [])
        for stmt in statements:
            principal = stmt.get("Principal", {})
            if isinstance(principal, dict) and "AWS" in principal:
                arn = principal["AWS"]
                if isinstance(arn, str) and ":iam::" in arn:
                    # Extract AWS account ID from ARN
                    parts = arn.split(":")
                    if len(parts) > 4:
                        return True, parts[4]

        return True, None

    except iam.exceptions.NoSuchEntityException:
        return False, None
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Control Tower): {e.response['Error']['Message']}")
        return False, None
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error (Control Tower): {str(e)}")
        return False, None

def get_landing_zone_info(client):
    '''
    Retrieve Control Tower landing zone information.
    '''
    landing_zones = client.list_landing_zones()
    if not landing_zones.get("LandingZones"):
        return None, None, None
    landing_zone = landing_zones["LandingZones"][0]
    return landing_zone["LandingZoneIdentifier"], landing_zone.get("HomeRegion", "UNKNOWN"), landing_zone.get("RootId", None)

def get_enrolled_accounts(ou_client):
    '''
    Retrieve enrolled AWS accounts.
    '''
    accounts = ou_client.list_accounts()
    enrolled_accounts = [acc for acc in accounts["Accounts"] if acc["Status"] == "ACTIVE"]
    return len(enrolled_accounts), len(accounts["Accounts"])

def get_control_settings(client, landing_zone_id):
    '''
    Retrieve various control settings.
    '''
    landing_zone_regions = client.list_landing_zone_regions(LandingZoneIdentifier=landing_zone_id)
    controls = client.list_enabled_controls(LandingZoneIdentifier=landing_zone_id)
    region_deny_enabled = any(control["ControlIdentifier"] == "AWS-REGIONS_DENY" for control in controls["EnabledControls"])
    return len(landing_zone_regions['Regions']), region_deny_enabled

def check_security_services(session):
    '''
    Check security-related AWS services (CloudTrail, IAM Identity Center, Backup).
    '''
    cloudtrail_client = session.client("cloudtrail")
    cloudtrails = cloudtrail_client.describe_trails()
    cloudtrail_enabled = any(trail['IsMultiRegionTrail'] for trail in cloudtrails['trailList'])

    identity_client = session.client("sso-admin")
    identity_status = identity_client.list_instances()
    identity_center_enabled = bool(identity_status['Instances'])

    backup_client = session.client("backup")
    backup_vaults = backup_client.list_backup_vaults()
    backup_enabled = len(backup_vaults['BackupVaultList']) > 0

    return cloudtrail_enabled, identity_center_enabled, backup_enabled

def validate_control_tower(session):
    '''
    Validate AWS Control Tower settings.
    '''
    print("\n🔍 Validating AWS Control Tower...")

    enabled, managing_account = check_controltower_service_enabled(session)
    if not enabled:
        print("⚠ AWS Control Tower Service is NOT Enabled")
        return

    print("✔ AWS Control Tower Service is Enabled")
    if managing_account:
        print(f"✔ This account is managed by Control Tower management account: {managing_account}")

    # Validate landing zones
    client = session.client("controltower")

    try:
        response = client.list_landing_zones()
        landing_zones = response.get("landingZones", [])
        if landing_zones:
            print(f"✔ Landing Zones found: {len(landing_zones)}")
        else:
            print("⚠ No Landing Zones found in Control Tower.")
    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Control Tower): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error (Control Tower): {str(e)}")

# pylint: disable=R0914
# def validate_control_tower(session):
#     '''
#     Validate AWS Control Tower settings.
#     '''
#     client = session.client("controltower")
#     try:
#         if not check_controltower_service_enabled(session):
#             print("⚠ AWS Control Tower Service is NOT Enabled")
#             return
#         print("✔ AWS Control Tower Service is Enabled")

#         landing_zone_id, home_region, root_id = get_landing_zone_info(client)
#         if not landing_zone_id:
#             print("⚠ No Landing Zones found in Control Tower.")
#             return

#         print(f"✔ Control Tower Landing Zone Identifier: {landing_zone_id}")
#         print(f"✔ Control Tower Home Region: {home_region}")

#         ou_client = session.client("organizations")
#         registered_ous = ou_client.list_organizational_units_for_parent(ParentId=root_id)
#         enrolled_count, total_accounts = get_enrolled_accounts(ou_client)
#         managed_regions, region_deny_enabled = get_control_settings(client, landing_zone_id)
#         cloudtrail_enabled, identity_center_enabled, backup_enabled = check_security_services(session)

#         print(f"✔ Registered Organizational Units (OUs): {len(registered_ous['OrganizationalUnits'])}")
#         print(f"✔ Enrolled Accounts: {enrolled_count}/{total_accounts}")
#         print(f"✔ Managed Landing Zone Regions: {managed_regions}")
#         print(f"✔ Region Deny Control Enabled: {region_deny_enabled}")
#         print(f"✔ AWS CloudTrail Enabled: {cloudtrail_enabled}")
#         print(f"✔ AWS IAM Identity Center Enabled: {identity_center_enabled}")
#         print(f"✔ AWS Backup Enabled: {backup_enabled}")

#     except botocore.exceptions.ClientError as e:
#         print(f"❌ AWS API Client error (Control Tower): {e.response['Error']['Message']}")
#         print(f"DEBUG: Full error response: {e.response}")
#     except botocore.exceptions.BotoCoreError as e:
#         print(f"❌ BotoCore error: {str(e)}")
