
from odoo import models, fields, api

class CrmCallDetail(models.Model):
    _name = 'crm.call.detail'
    _description = 'CRM Call Details'
    _order = 'call_date desc, id desc'
    
    lead_id = fields.Many2one(
        'crm.lead', 
        string='Lead/Opportunity', 
        required=True, 
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        default=lambda self: self.env.user,
        required=True
    )
    call_date = fields.Datetime(
        string='Call Date', 
        default=fields.Datetime.now,
        required=True
    )
    call_timing = fields.Selection([
        ('morning', 'Morning (9 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 5 PM)'),
        ('evening', 'Evening (5 PM - 9 PM)'),
    ], string='Call Timing', required=True)
    
    duration = fields.Float(
        string='Duration (minutes)', 
        help='Call duration in minutes'
    )
    subject = fields.Char(string='Subject')
    notes = fields.Text(string='Notes')
    call_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('missed', 'Missed'),
    ], string='Call Type', default='outgoing')
    
    @api.onchange('call_date')
    def _onchange_call_date(self):
        """Auto-set call timing based on call date"""
        if self.call_date:
            hour = self.call_date.hour
            if 9 <= hour < 12:
                self.call_timing = 'morning'
            elif 12 <= hour < 17:
                self.call_timing = 'afternoon'
            elif 17 <= hour < 21:
                self.call_timing = 'evening'




