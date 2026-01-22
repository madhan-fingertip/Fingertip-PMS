from odoo import models, fields, api

class MarketingScorecard(models.Model):
    _name = "marketing.scorecard"
    _description = "Marketing Scorecard"
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

    videos = fields.Integer(string="Videos")
    posts = fields.Integer(string="Posts")
    leads = fields.Integer(string="Leads")
    
    @api.depends('date')
    def _compute_name(self):
        for record in self:
            if record.date:
                record.name = f"Marketing Scorecard - {record.date}"
            else:
                record.name = "Marketing Scorecard"

