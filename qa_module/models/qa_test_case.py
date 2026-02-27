from odoo import models, fields, api


class QATestCase(models.Model):
    _name = 'qa.test.case'
    _description = 'QA Test Case'
    _order = 's_no'

    s_no = fields.Integer(string='S No', required=True)
    test_case_id = fields.Char(string='Test Case ID', required=True)
    test_case_title = fields.Char(string='Test Case Title', required=True)
    module = fields.Char(string='Module', required=True)
    project_id = fields.Many2one('project.project', string='Project')
    project_org_id = fields.Many2one('res.partner', string='Project ORG ID')
    test_objective = fields.Text(string='Test Objective')
    pre_conditions = fields.Text(string='Pre Conditions')
    test_data = fields.Text(string='Test Data (Input values)')
    test_steps = fields.Text(string='Test Steps')
    expected_result = fields.Text(string='Expected Result')
    actual_result = fields.Text(string='Actual Result')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('blocked', 'Blocked'),
        ('not_executed', 'Not Executed')
    ], string='Status', default='not_executed')
    severity = fields.Selection([
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], string='Severity', default='medium')
    environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], string='Environment', default='sandbox')
    executed_date = fields.Date(string='Executed Date')
    executed_by = fields.Many2one('res.users', string='Executed By')
    test_type = fields.Selection([
        ('smoke', 'Smoke'),
        ('uat', 'UAT'),
        ('regression', 'Regression')
    ], string='Test Type', default='smoke')
