# aws-assess
Scan an AWS Environment for initial assessment data.

## Goals

Produce a report to inform the user of the level of maturity of the target AWS environment

## Anatomy of a scan

Validate the following information:

- Account
    - Billing Config
    - Contact Info
- IAM
    - IAM User Settings
    - IAM User Count in-use
    - Roles: Customer Managed in-use
    - IDP Settings
- Organizations
    - Part of an Org?
        - Standalone or in an Organization
    - Member
        - Member of OrgID
    - Manager
        - List member account numbers with names
    - Delegated Admin settings
- Control Tower
    - Enabled
    - Security Audit Account
    - Security Logging Account
    - IAM Identity Management Settings
- Config
    - Enabled
    - Consolidated
- Security Hub
    - Enabled
    - Consolidation settings
- Inspector
    - Enabled
    - Consolidation settings
    - Service coverage
    - Sending to Security Hub
- Guard Duty
    - Enabled
    - Consolidation settings
    - Service coverage
    - Sending to Security Hub
- Access Analyzer
    - External Access monitoring enabled
    - Unused Access monitoring enabled
- Macie
    - Enabled
    - Consolidation settings
    - Service coverage
    - Sending to Security Hub
    - Secrets management configured

## Reporting Methods

By default, output will be `stdout`. Additional outputs can include:
- slack
- email
- teams
- jira tickets (for outstanding tasks)

## Methodology

There are two options.

1. Scan through the essential settings and stop before going deep.
2. Scan through all settings and produce a gap report.

Think about which will be better once data becomes avaialble.
