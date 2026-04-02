from odoo import models, fields, api


class QATestCase(models.Model):
    _name = 'qa_testapp.test_case'
    _description = 'QA Test Case'
    _order = 'id desc'
    _rec_name = 'test_case_id'

    test_case_id = fields.Char(string='Test Case ID', readonly=True, copy=False, default='New')
    test_case_title = fields.Char(string='Test Case Title', required=True)
    module = fields.Char(string='Module', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    test_objective = fields.Text(string='Test Objective')
    pre_conditions = fields.Text(string='Pre Conditions')
    test_data = fields.Text(string='Test Data')
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
        ('qa', 'QA'),
        ('production', 'Production')
    ], string='Environment', default='sandbox')
    executed_date = fields.Date(string='Executed Date')
    executed_by = fields.Many2one('res.users', string='Executed By')
    test_type = fields.Selection([
        ('smoke', 'Smoke'),
        ('functional', 'Functional'),
        ('uat', 'UAT'),
        ('regression', 'Regression')
    ], string='Test Type', default='smoke')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('test_case_id', 'New') == 'New':
                vals['test_case_id'] = self.env['ir.sequence'].next_by_code('qa_testapp.test_case') or 'New'
        return super().create(vals_list)
