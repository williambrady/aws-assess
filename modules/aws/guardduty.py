'''
This module is responsible for validating AWS GuardDuty settings.
modules/aws/guardduty.py
'''
# import json
import botocore.exceptions

def validate_guardduty(session):
    '''
    Validate GuardDuty configuration in a specific region.
    '''
    region = session.region_name

    us_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]
    checked_regions = set()

    def perform_check(region_to_check):
        try:
            client = session.client("guardduty", region_name=region_to_check)
            detectors = client.list_detectors()["DetectorIds"]
            if not detectors:
                print(f"⚠ No GuardDuty detectors found in {region_to_check}.")
                return

            detector_id = detectors[0]
            response = client.get_detector(DetectorId=detector_id)

            print(f"✔ GuardDuty is Enabled in {region_to_check}")
            # print(f"DEBUG: Detector ID: {json.dumps(response, default=str, indent=2)}")

            # Consolidation config (frequency of publishing findings)
            frequency = response.get("FindingPublishingFrequency", "UNKNOWN")
            print(f"✔ Consolidation (Enable): {frequency}")

            # Service coverage check
            coverage = response.get("DataSources", {})
            print("✔ GuardDuty Service Coverage:")
            print(f"  - CloudTrail: {coverage.get('CloudTrail', {}).get('Status', 'DISABLED')}")
            print(f"  - DNSLogs: {coverage.get('DNSLogs', {}).get('Status', 'DISABLED')}")
            print(f"  - FlowLogs: {coverage.get('FlowLogs', {}).get('Status', 'DISABLED')}")
            print(f"  - S3Logs: {coverage.get('S3Logs', {}).get('Status', 'DISABLED')}")
            print(f"  - Kubernetes: {coverage.get('Kubernetes', {}).get('AuditLogs', {}).get('Status', 'DISABLED')}")
            print(f"  - MalwareProtection: {coverage.get('MalwareProtection', {}).get('ScanEc2InstanceWithFindings', {}).get('EbsVolumes', {}).get('Status', 'DISABLED')}")

        except botocore.exceptions.ClientError as e:
            print(f"❌ AWS API Client error (GuardDuty - {region_to_check}): {e.response['Error']['Message']}")
        except botocore.exceptions.BotoCoreError as e:
            print(f"❌ BotoCore error (GuardDuty - {region_to_check}): {str(e)}")

    # Check default region first
    perform_check(region)
    checked_regions.add(region)

    # Check remaining regions
    for r in us_regions:
        if r not in checked_regions:
            perform_check(r)

    session = None
