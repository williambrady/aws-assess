# aws-assess
Scan an AWS Environment for initial assessment data.

## Goals

Produce a report to inform the user of the level of maturity of the target AWS environment

## Anatomy of a scan

Validate the following information:

- Account
    - Account Contact Config
    - Contact Info
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
    - Is it Enabled?
    - Identify the Security Audit Account
    - Identify the Security Logging Account
    - IAM Identity Management Settings
- Config
    - Is it Enabled?
    - Confirm there is an aggregator with Source Type of My organization
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
