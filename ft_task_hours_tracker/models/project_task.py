from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    ft_total_hours_taken = fields.Float(
        string='Total Hours Taken',
        compute='_compute_ft_total_hours_taken',
        store=True,
        readonly=True,
        help='Mirrors the standard Hours Spent (effective_hours) for this task.',
    )
    ft_hours_exceeded = fields.Boolean(
        string='Exceeds Time Limit',
        compute='_compute_ft_total_hours_taken',
        store=True,
        help='True when Total Hours Taken exceeds the global task time limit.',
    )
    ft_allow_billable = fields.Boolean(
        related='project_id.allow_billable',
        string='Is Billable Project',
        store=False,
    )

    # Department bucket of the LOGGED-IN user. Drives which label is shown for
    # the "Actual Hours" field on the task form: Dev / QA / PM. Not stored - it
    # is per-user, recomputed from the current user's employee department.
    current_user_dept_type = fields.Selection(
        [('dev', 'Development'), ('qa', 'QA'), ('pm', 'PM')],
        string='Current User Department Type',
        compute='_compute_current_user_dept_type',
    )

    @api.depends_context('uid')
    def _compute_current_user_dept_type(self):
        department = self.env.user.employee_id.department_id
        dept_name = (department.name or '').strip().lower()
        dept_type = False
        if 'development' in dept_name:
            dept_type = 'dev'
        elif 'testing' in dept_name or dept_name == 'qa':
            dept_type = 'qa'
        elif 'project management' in dept_name or dept_name == 'pm':
            dept_type = 'pm'
        for task in self:
            task.current_user_dept_type = dept_type

    @api.depends('effective_hours')
    def _compute_ft_total_hours_taken(self):
        time_limit = float(
            self.env['ir.config_parameter'].sudo().get_param(
                'ft_task_hours_tracker.default_time_limit', default=0.0
            )
        )
        for task in self:
            total = task.effective_hours
            task.ft_total_hours_taken = total
            task.ft_hours_exceeded = time_limit > 0 and total > time_limit
