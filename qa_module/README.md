# QA Module for Odoo 18

## Overview
This module provides comprehensive Quality Assurance functionality for managing test plans, test scenarios, and test cases in Odoo 18.

## Features

### Test Plan
Manage comprehensive test plans with the following fields:
- Project ORG ID
- Introduction (Purpose)
- Test Objectives (Quality Goals)
- Scope (In scope and Out of scope)
- Test Approach (Test types/Test Level)
- Test Environment
- Test Schedule (Activity Start Date and End Date)
- Entry and Exit Criteria
- Roles and Responsibilities (Test Manager, Test Engineer, Developer)
- Defect Management
- Assumptions and Constraints
- Approval (Approval Authority and Sign off details)

### Test Scenario
Track test scenarios with:
- S No
- Date
- Test Scenario ID
- Module
- Description
- Status: Pass/Fail/Invalid
- Comments (to be filled by PM)
- Created By
- Reviewed By
- Project

### Test Case
Detailed test case management including:
- S No
- Test Case ID
- Test Case Title
- Module
- Test Objective
- Pre Conditions
- Test Data (Input values)
- Test Steps
- Expected Result
- Actual Result
- Status
- Severity
- Environment: Sandbox/Production
- Executed Date
- Executed By
- Test Type: Smoke/UAT/Regression

## Installation

1. Copy the `qa_module` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "QA Module" from the Apps menu

## Usage

After installation, you will find a new "QA" menu in the main navigation bar with three sub-menus:
- Test Plan
- Test Scenario
- Test Case

Navigate to each menu to create and manage your QA artifacts.

## Technical Details

- **Version**: 18.0.1.0.0
- **Depends on**: base, project
- **License**: LGPL-3

## Models

- `qa.test.plan`: Test Plan model
- `qa.test.scenario`: Test Scenario model
- `qa.test.case`: Test Case model

## Security

Access rights are granted to all users (base.group_user) for read, write, create, and delete operations on all models.

**Note**: By default, all authenticated users have full access to QA records. If you need more granular control:
1. Create custom security groups (e.g., QA Manager, QA Tester)
2. Update `security/ir.model.access.csv` to assign different permissions to each group
3. Consider adding record rules for row-level security if needed
