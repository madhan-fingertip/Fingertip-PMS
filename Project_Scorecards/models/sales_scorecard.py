from odoo import models, fields, api

class SalesScorecard(models.Model):
    _name = "sales.scorecard"
    _description = "Sales Scorecard"
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

    new_leads = fields.Integer(string="New Leads")
    proposals = fields.Integer(string="Proposals")
    closed = fields.Integer(string="Closed")
    closed_amount = fields.Float(string="Closed Amount")

    def _compute_name(self):
        for record in self:
            record.name = "Sales Scorecard"
