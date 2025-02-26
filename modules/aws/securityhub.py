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
    client = session.client("securityhub")

    try:
        hub_status = client.describe_hub()
        print("✔ AWS Security Hub is Enabled")

        get_security_hub_standards(client)
        get_security_hub_integrations(client)
        check_automation_rules(client)

        print(f"✔ Auto-enable new controls: {hub_status.get('AutoEnableControls', False)}")
        print(f"✔ Consolidated Control Findings: {hub_status.get('ControlFindingGenerator', 'NOT SET')}")

        # Retrieve finding aggregators
        finding_aggregators = client.list_finding_aggregators().get("FindingAggregators", [])

        if finding_aggregators:
            for aggregator in finding_aggregators:
                aggregator_arn = aggregator.get("FindingAggregatorArn")
                if aggregator_arn:
                    # Query details about the aggregator
                    aggregator_details = client.get_finding_aggregator(FindingAggregatorArn=aggregator_arn)
                    finding_aggregation_region = aggregator_details.get("FindingAggregationRegion", "Unknown")
                    region_linking_mode = aggregator_details.get("RegionLinkingMode", "Unknown")
                    linked_regions = aggregator_details.get("Regions", [])

                    print("✔ Security Hub Aggregation Details:")
                    print(f"  - Finding Aggregation Region: {finding_aggregation_region}")
                    print(f"  - Region Linking Mode: {region_linking_mode}")
                    print("  - Linked Regions:")
                    for region in sorted(linked_regions):
                        print(f"    - {region}")

    except botocore.exceptions.ClientError as e:
        print(f"❌ AWS API Client error (Security Hub): {e.response['Error']['Message']}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ BotoCore error: {str(e)}")
    finally:
        session = None
