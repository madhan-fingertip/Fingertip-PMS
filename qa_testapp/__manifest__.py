{
    'name': 'QA TestApp – Test & Bug Tracker',
    'version': '18.0.1.0.0',
    'category': 'Quality Assurance',
    'summary': 'Test Plans, Scenarios, Test Cases & Bug Tickets — all-in-one QA suite',
    'description': """
QA TestApp – Test & Bug Tracker
===============================
A comprehensive Quality Assurance suite for Odoo 18 with:
 * Test Plan management (scope, objectives, approach, schedule, approval)
 * Test Scenario tracking (steps, coverage, status)
 * Test Case execution (data, preconditions, steps, actual/expected, severity)
 * Bug/Ticket tracking (Bug ID, reporter, description, reproducibility, attachments — full ticket lifecycle)
""",
    'author': 'Fingertip',
    'website': '',
    'depends': ['base', 'project', 'mail'],
    'data': [
            'security/ir.model.access.csv',
            'data/ticket_sequence.xml',
            'views/test_plan_views.xml',
            'views/test_scenario_views.xml',
            'views/test_case_views.xml',
            'views/ticket_views.xml',  
            'views/menu.xml',
        ],
    'static': ['static/description/icon.svg'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}