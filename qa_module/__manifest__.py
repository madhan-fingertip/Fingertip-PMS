{
    'name': 'QA Module',
    'version': '18.0.1.0.0',
    'category': 'Quality Assurance',
    'summary': 'QA Module for Test Plans, Test Scenarios and Test Cases',
    'description': """
        QA Module
        =========
        This module provides comprehensive Quality Assurance functionality including:
        * Test Plans
        * Test Scenarios
        * Test Cases
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/qa_test_plan_views.xml',
        'views/qa_test_scenario_views.xml',
        'views/qa_test_case_views.xml',
        'views/qa_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
