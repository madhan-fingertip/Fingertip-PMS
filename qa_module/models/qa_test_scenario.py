from odoo import models, fields, api


class QATestScenario(models.Model):
    _name = 'qa.test.scenario'
    _description = 'QA Test Scenario'
    _order = 's_no'

    s_no = fields.Integer(string='S No', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    test_scenario_id = fields.Char(string='Test Scenario ID', required=True)
    module = fields.Char(string='Module', required=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('invalid', 'Invalid')
    ], string='Status', default='pass')
    comments = fields.Text(string='Comments', help='Comments needs to be filled by PM')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    project_id = fields.Many2one('project.project', string='Project')
    project_org_id = fields.Many2one('res.partner', string='Project ORG ID')
