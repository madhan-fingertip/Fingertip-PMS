from odoo import models, fields, api

class HRTrainingScorecard(models.Model):
    _name = "hr.training.scorecard"
    _description = "HR Training Scorecard"
    _rec_name = "name"

    name = fields.Char(
        string="Scorecard Name",
        compute="_compute_name",
        store=True
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today
    )

    department = fields.Selection([
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('operations', 'Operations'),
        ('hr', 'HR'),
        ('finance', 'Finance'),
    ], string="Department", required=True)

    subject = fields.Char(string="Subject")
    description = fields.Text(string="Description")

    def _compute_name(self):
        dept_labels = dict(self.fields_get(allfields=['department'])['department']['selection'])
        for record in self:
            dept = dept_labels.get(record.department, '')
            subject = record.subject or ''
            record.name = f"HR Training - {dept} - {subject}".strip(' -')
