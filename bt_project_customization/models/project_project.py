from odoo import models, fields,api


class InheritProjectProject(models.Model):
    _inherit = 'project.project'

    architect_id = fields.Many2one('res.users', string='Architect')
    ba_id = fields.Many2one('res.users', string='BA')
    pm_id = fields.Many2one('res.users', string='PM')
    brd_approval_date = fields.Date(string='BRD Approval Date')
    brd_submission_date = fields.Date(string='BRD Submission Date')
    go_live_date = fields.Date(string='Go Live Date')
    # end_date = fields.Date(string='End Date')
    kick_start_meeting_date = fields.Date(string='Kick Start Meeting Date')
    sandbox_review_date = fields.Date(string='Sandbox Review Date')
    # start_date = fields.Date(string='Start Date')
    support_start_date = fields.Date(string='Support Start Date')
    uat_start_date = fields.Date(string='UAT Start Date')
    warranty_end_date = fields.Date(string='Warranty End Date')
    comments = fields.Text(string='Comments')
    development = fields.Text(string='Development')
    payment_terms = fields.Text(string='Payment Terms')
    payment_terms_id = fields.Many2one('account.payment.term',string='Payment Terms')
    user_name = fields.Char(string='User Name')
    password = fields.Char(string='Password')
    poc_email = fields.Char(string='POC Email')
    poc_mobile = fields.Char(string='POC Mobile')
    short_code = fields.Char(string='Short Code', help='Unique, case insensitive')
    hourly_billing_rate = fields.Monetary(string='Hourly Billing Rate', currency_field='currency_id')
    hourly_cost = fields.Monetary(string='Hourly Cost', currency_field='currency_id')
    hours_balance = fields.Float(string='Hours Balance')
    hours_est_pm = fields.Float(string='Hours Est PM')
    hours_est_qa = fields.Float(string='Hours Est QA')
    hours_est_dev = fields.Float(string='Hours Est Dev')
    hours_overflowed = fields.Float(string='Hours Overflowed')
    hours_spent_dev = fields.Float(string='Hours Spent Dev')
    hours_spent_pm = fields.Float(string='Hours Spent PM')
    hours_spent_qa = fields.Float(string='Hours Spent QA')
    stories = fields.Float(string='Stories')
    status = fields.Selection([
        ('discovery', 'Discovery'),
        ('development', 'Development'),
        ('sandbox_review', 'Sandbox Review'),
        ('regression_testing', 'Regression Testing'),
        ('deployment', 'Deployment'),
        ('data_upload', 'Data Upload'),
        ('user_acceptance', 'User Acceptance'),
        ('training', 'Training'),
        ('support', 'Support'),
        ('amc', 'AMC'),
        ('closed', 'Closed'),
        ('hold', 'Hold'),
    ], string='Status')
    sync_wc = fields.Boolean(string='Sync WC')
    wc_id = fields.Char(string='Wc Id')

    timesheet_count = fields.Float(
        string="Timesheet Hours",
        compute='_compute_timesheet_count'
    )

    def _compute_timesheet_count(self):
        for project in self:
            lines = self.env['account.analytic.line'].search([('project_id', '=', project.id)])
            project.timesheet_count = sum(lines.mapped('unit_amount'))

    def action_view_timesheets(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.timesheet_action_all')
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'search_default_project_id': self.id,
            'group_by': [ 'jobposition_id', 'employee_id','task_id'],
        }
        return action


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    jobposition_id = fields.Many2one(
        'hr.job',
        string="Job Position",
        readonly=False,
    )

    @api.onchange('jobposition_id')
    def _onchange_jobposition_id(self):
        if self.jobposition_id:
            self.employee_id.job_id = self.jobposition_id


    # @api.depends('employee_id.job_id')
    # def _compute_jobposition_id(self):
    #     """
    #     Compute: Sync from Employee -> Timesheet
    #     When the employee's job_id changes, update the timesheet jobposition_id.
    #     """
    #     for line in self:
    #         if line.employee_id and line._get_job_update_needed():
    #             line.jobposition_id = line.employee_id.job_id
    #         else:
    #             # Clear if no employee
    #             line.jobposition_id = False
    #
    # def _inverse_jobposition_id(self):
    #     """
    #     Inverse: Sync from Timesheet -> Employee
    #     When jobposition_id changes on the timesheet, update the employee's job_id.
    #     """
    #     for line in self:
    #         if line.employee_id and line._get_job_update_needed():
    #             line.employee_id.job_id = line.jobposition_id or False
    #
    # def _get_job_update_needed(self):
    #     """
    #     Helper method to check whether the timesheet job position
    #     and the employee's job position are different.
    #     This prevents infinite loops and unnecessary writes.
    #     """
    #     self.ensure_one()
    #     return self.employee_id and self.jobposition_id != self.employee_id.job_id

