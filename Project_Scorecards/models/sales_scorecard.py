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


    emails = fields.Integer(string="Emails")
    whatsapp = fields.Integer(string="WhatsApp")
    connected_calls = fields.Integer(string="Connected Calls")
    call_duration = fields.Float(string="Call Duration (Hours)")

    @api.depends('date')
    def _compute_name(self):
        for record in self:
            if record.date:
                record.name = f"Sales Scorecard - {record.date}"
            else:
                record.name = "Sales Scorecard"

