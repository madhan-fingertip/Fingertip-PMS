from odoo import models, fields, api

class ProjectScorecard(models.Model):
    _name = "project.scorecard"
    _description = "Project Scorecard"
    _rec_name = "name"

    name = fields.Char(
        string="Scorecard Name",
        compute="_compute_name",
        store=True
    )

    date = fields.Date(
        string="Date",
        default=fields.Date.context_today
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade"
    )

    meetings = fields.Integer(string="Meetings")

    # ONLY TIME FIELD
    time_spent = fields.Float(
        string="Time",
        help="Time in hours"
    )

    @api.depends("project_id")
    def _compute_name(self):
        for record in self:
            record.name = (
                f"{record.project_id.name} - Project Scorecard"
                if record.project_id else
                "Project Scorecard"
            )
