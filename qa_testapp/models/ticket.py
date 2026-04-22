from odoo import models, fields, api

class QATicket(models.Model):
    _name = 'qa_testapp.ticket'
    _description = 'QA Bug Ticket'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'title'

    bug_id = fields.Char(string='Bug ID', readonly=True, copy=False, default='New', tracking=True)
    title = fields.Char(string='Title / Summary', required=True, tracking=True,
                        help="One-line specific summary, e.g., 'Login fails with 500 when password contains #'.")
    description = fields.Text(string='Description', help="What's wrong + what you expected.")
    steps_to_reproduce = fields.Text(string='Steps to Reproduce', help="Numbered steps.")
    expected_result = fields.Text(string='Expected Result')
    actual_result = fields.Text(string='Actual Result')
    environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('qa', 'QA'),
        ('production', 'Production')
    ], string='Environment', default='sandbox', required=True)
    device = fields.Selection([
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet')
    ], string='Device', default='desktop')
    severity = fields.Selection([
        ('blocker', 'Blocker'),
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('trivial', 'Trivial')
    ], string='Severity', default='major', tracking=True)
    priority = fields.Selection([
        ('p0', 'P0 - Urgent'),
        ('p1', 'P1 - High'),
        ('p2', 'P2 - Medium'),
        ('p3', 'P3 - Low'),
        ('p4', 'P4 - Backlog')
    ], string='Priority', default='p2', tracking=True)
    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('fixed', 'Fixed'),
        ('closed', 'Closed'),
        ('reopened', 'Re-Opened')
    ], string='Status', default='open', tracking=True)
    reproducibility = fields.Selection([
        ('always', 'Always'),
        ('sometimes', 'Sometimes'),
        ('rare', 'Rare'),
        ('unable', 'Unable to Reproduce')
    ], string='Reproducibility', default='always')
    evidence_notes = fields.Text(string='Evidence Notes')
    evidence_attachment_ids = fields.Many2many(
        'ir.attachment', 'qa_testapp_ticket_attachment_rel',
        'ticket_id', 'attachment_id',
        string='Attachments',
    )
    reporter_id = fields.Many2one('res.users', string='Reporter', default=lambda self: self.env.user, tracking=True)
    reported_date = fields.Datetime(string='Reported Date', default=fields.Datetime.now)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    module = fields.Char(string='Module (legacy)', tracking=True)
    module_id = fields.Many2one(
        'cus.module',
        string='Module',
        tracking=True,
        help='Module used on a task of the selected project.',
    )
    test_case_id = fields.Many2one('qa_testapp.test_case', string='Related Test Case')
    assignee_id = fields.Many2one('res.users', string='Assignee', required=True, tracking=True)

    def action_in_progress(self):
        self.write({'status': 'in_progress'})

    def action_fixed(self):
        self.write({'status': 'fixed'})

    def action_closed(self):
        self.write({'status': 'closed'})

    def action_reopen(self):
        self.write({'status': 'reopened'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('bug_id', 'New') == 'New':
                vals['bug_id'] = self.env['ir.sequence'].next_by_code('qa_testapp.ticket') or 'New'
        return super().create(vals_list)