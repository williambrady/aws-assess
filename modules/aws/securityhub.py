'''
This module is responsible for validating AWS Security Hub settings.
modules/aws/securityhub.py
'''
import botocore.exceptions

def check_automation_rules(client):
    '''
    Check the number of Security Hub automation rules.
    '''
    try:
        automation_rules = client.list_automation_rules(MaxResults=100).get("AutomationRulesMetadata", [])
        print(f"{'✔' if len(automation_rules) == 0 else '⚠'} Security Hub Automations: {len(automation_rules)}")
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ValidationException":
            print("⚠ Security Hub Automations are not supported in this account.")
        elif error_code == "AccessDeniedException":
            print("⚠ Access denied: Security Hub Automations are only available in the Delegated Admin account.")
        else:
            print(f"❌ AWS API Client error (Security Hub Automations): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")

def get_security_hub_standards(client):
    '''
    Retrieve and print enabled Security Hub standards.
    '''
    standards_subscriptions = client.get_enabled_standards().get("StandardsSubscriptions", [])
    enabled_standards = sorted([
        f"{s['StandardsArn'].split('/')[-3]} {s['StandardsArn'].split('/')[-1]}"
        for s in standards_subscriptions
    ])
    print("✔ Enabled Security Hub Standards:")
    for standard in enabled_standards:
        print(f"  - {standard}")

def get_security_hub_integrations(client):
    '''
    Retrieve and print enabled Security Hub integrations.
    '''
    integrations_subscriptions = client.list_enabled_products_for_import().get("ProductSubscriptions", [])
    enabled_integrations = sorted([
        arn.split("/")[-1] for arn in integrations_subscriptions if isinstance(arn, str)
    ])
    if enabled_integrations:
        print("✔ Enabled Security Hub Integrations:")
        for integration in enabled_integrations:
            print(f"  - {integration}")
    else:
        print("⚠ No Security Hub Integrations found.")

def validate_security_hub(session):
    '''
    Validate AWS Security Hub settings.
    '''
    region = session.region_name

    us_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]
    checked_regions = set()

    def perform_check(region_to_check):
        try:
            temp_client = session.client("securityhub", region_name=region_to_check)
            hub_status = temp_client.describe_hub()
            print(f"✔ AWS Security Hub is Enabled in {region_to_check}")

            get_security_hub_standards(temp_client)
            get_security_hub_integrations(temp_client)
            check_automation_rules(temp_client)

            print(f"✔ Auto-enable new controls: {hub_status.get('AutoEnableControls', False)}")
            print(f"✔ Consolidated Control Findings: {hub_status.get('ControlFindingGenerator', 'NOT SET')}")

            finding_aggregators = temp_client.list_finding_aggregators().get("FindingAggregators", [])
            if finding_aggregators:
                for aggregator in finding_aggregators:
                    aggregator_arn = aggregator.get("FindingAggregatorArn")
                    if aggregator_arn:
                        aggregator_details = temp_client.get_finding_aggregator(FindingAggregatorArn=aggregator_arn)
                        print("✔ Security Hub Aggregation Details:")
                        print(f"  - Finding Aggregation Region: {aggregator_details.get('FindingAggregationRegion', 'Unknown')}")
                        print(f"  - Region Linking Mode: {aggregator_details.get('RegionLinkingMode', 'Unknown')}")
                        for r in sorted(aggregator_details.get('Regions', [])):
                            print(f"    - {r}")
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ["ResourceNotFoundException", "InvalidAccessException"]:
                print(f"⚠ AWS Security Hub is not enabled in {region_to_check}")
            else:
                print(f"❌ AWS API Client error (Security Hub - {region_to_check}): {e.response['Error']['Message']}")
        except botocore.exceptions.BotoCoreError as e:
            print(f"❌ BotoCore error (Security Hub - {region_to_check}): {str(e)}")

    # Check default region first
    perform_check(region)
    checked_regions.add(region)

    # Check remaining US regions
    for r in us_regions:
        if r not in checked_regions:
            perform_check(r)

    session = None
