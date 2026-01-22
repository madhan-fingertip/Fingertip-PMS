from odoo import models, fields, api

class HRRecruitmentScorecard(models.Model):
    _name = "hr.recruitment.scorecard"
    _description = "HR Recruitment Scorecard"
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

    positions = fields.Integer(string="Positions")
    description = fields.Text(string="Description")

    def _compute_name(self):
        dept_labels = dict(self.fields_get(allfields=['department'])['department']['selection'])
        for record in self:
            record.name = f"HR Recruitment - {dept_labels.get(record.department, '')}"
