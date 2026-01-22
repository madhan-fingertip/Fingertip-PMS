from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    call_detail_ids = fields.One2many(
        'crm.call.detail', 
        'lead_id', 
        string='Call Details'
    )
    call_count = fields.Integer(
        string='Call Count', 
        compute='_compute_call_count'
    )
    last_call_date = fields.Datetime(
        string='Last Call Date',
        compute='_compute_last_call_date',
        store=True
    )


    custom_status = fields.Selection([
        ('new', 'New'),
        ('rnr', 'RNR'),
        ('follow_up', 'Follow Up'),
        ('site_visit', 'Site Visit Scheduled'),
    ], string='Status', default='new', tracking=True, required=True)

    @api.model
    def create(self, vals):
        if 'custom_status' not in vals:
            vals['custom_status'] = 'new'
        return super(CrmLead, self).create(vals)

    def action_set_new(self):
        self.write({'custom_status': 'new'})

    def action_set_rnr(self):
        self.write({'custom_status': 'rnr'})

    def action_set_follow_up(self):
        self.write({'custom_status': 'follow_up'})

    def action_set_site_visit(self):
        self.write({'custom_status': 'site_visit'})
    
    @api.depends('call_detail_ids')
    def _compute_call_count(self):
        for record in self:
            record.call_count = len(record.call_detail_ids)
    
    @api.depends('call_detail_ids.call_date')
    def _compute_last_call_date(self):
        for record in self:
            if record.call_detail_ids:
                record.last_call_date = max(record.call_detail_ids.mapped('call_date'))
            else:
                record.last_call_date = False
    
    def action_view_calls(self):
        """Open call details in a separate view"""
        self.ensure_one()
        return {
            'name': 'Call Details',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.call.detail',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
