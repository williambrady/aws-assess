# aws-assess
Scan an AWS Environment for initial assessment data.

## Goals

Produce a report to inform the user of the level of maturity of the target AWS environment

## Anatomy of a scan

Validate the following information:

- Account
    - Account Contact Config
    - Contact Info
    - Billing Summary
        - Which level of Support is enabled?
        - Which services are in use?
        - Which accounts are linked to this payer?
        - Are there any linked accounts that are not in the Organization?
        - Which regions have spend greater than $0? Treat Global as a region
- IAM
    - IAM User Settings
        - Password settings
            - Minimum Password Length
                - If 16 or greater return a checkmark with the value
                - If less than 16 return a warning icon with the value
            - Password strength (Enabled is good, if not it's bad)
                - Require at least one uppercase letter from the Latin alphabet (A-Z)
                - Require at least one lowercase letter from the Latin alphabet (a-z)
                - Require at least one number
                - Require at least one non-alphanumeric character ( ! @ # $ % ^ & * ( ) _ + - = [ ] {} | ' )
            - Other requirements
                - Turn on password expiration
                - Expire password in 90 day(s) (report this value, 90 or greater is good, less than 90 is bad)
                - Password expiration requires administrator reset
                - Allow users to change their own password
                - Prevent password reuse
                - Remember 24 password(s) (Less than 24 is bad, 24 or more is good)
    - IAM User Count in-use
        - If IAM User count !=0 then how many do not have MFA
        - If IAM User count !=0 then how many IAM users have Access Keys over 90 days old
        - If IAM User count !=0 then how many have not been accessed in the last 30 days
        - If IAM User count !=0 then how many have never logged in
    - Roles: Customer Managed in-use
    - [TODO] IDP Settings
- Organizations
    - Part of an Org?
        - Standalone or in an Organization
    - Member
        - Member of OrgID
    - Manager
        - List member account numbers with names
    - Delegated Admin settings
- Control Tower
    - Is it Enabled?
    - Identify the Security Audit Account
    - Identify the Security Logging Account
    - IAM Identity Management Settings
- Config
    - Is it Enabled?
    - Confirm there is an aggregator with Source Type of My organization
- Security Hub
    - Is it Enabled?
        - Check all US regions.
    - Policy check, which Standards are enabled?
    - Integrations, which are enabled?
    - Number of Automations: 0 is checkmark, greater than 0 is a warning
    - Controls: Auto-enable new controls?
    - Controls: Consolidated control findings?
    - Enabled Regions
        - Home region
        - Additional regions
    - [TODO] Is a Central policy Enabled?
- Inspector
    - Is it Enabled?
    - Account management
        - Is "Automatically activate Inspector for new member accounts" enabled?
        - Amazon EC2 scanning Enabled?
        - Amazon ECR scanning Enabled?
        - AWS Lambda standard scanning
        - AWS Lambda code scanning
        - [TODO] Count of Accounts where Status is Activated / Count of total accounts in Org
- [TODO] Guard Duty
    - Is it Enabled?
    - Is S3 Protection enabled?
    - Is EKS Protection enabled?
    - Is Extended Threat Detection enabled?
    - Is Runtime monitoring enabled?
    - Is Malware Protection for EC2 enabled?
    - Is Malware Protection for S3 enabled?
    - Is RDS Protection enabled?
    - Is Lambda Protection enabled?
- [TODO] Access Analyzer
    - Is External Access monitoring enabled
        - Excluded Accounts
        - Excluded IAM Users and Roles
        - Archive rules
    - Is Unused Access monitoring enabled
        - Excluded Accounts
        - Excluded IAM Users and Roles
        - Archive rules
- [TODO] Macie
    - Is it Enabled?
    - New Accounts: Is it enabled automatically?
    - New Accounts: Is Automated sensitive data discovery enabled?


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

## Assets

```
.
├── aws_assessment.py
├── cloudformation
│   └── cfn-role-security-operations.yaml
├── config.yaml
├── .editorconfig
├── .github
│   └── workflows
│       ├── lint_on_pull_request.yaml
│       └── lint_on_push.yaml
├── .gitignore
├── modules
│   ├── aws
│   │   ├── account.py
│   │   ├── config.py
│   │   ├── controltower.py
│   │   ├── guardduty.py
│   │   ├── iam.py
│   │   ├── __init__.py
│   │   ├── inspector.py
│   │   ├── macie.py
│   │   ├── organizations.py
│   │   └── securityhub.py
│   ├── config.py
│   ├── __init__.py
│   ├── jira
│   │   ├── __init__.py
│   │   └── jira.py
│   ├── o365
│   │   ├── __init__.py
│   │   └── teams.py
│   └── slack
│       ├── __init__.py
│       └── slack.py
└── README.md
```
