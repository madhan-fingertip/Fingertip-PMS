from odoo import models, fields, api

import base64
from io import BytesIO

class FollowUp(models.Model):
    _name = 'follow.up'
    _description = 'Follow Up'
    _rec_name = 'name'

    name = fields.Char(string='Follow Up Id', required=True, copy=False,
                       default=lambda self: 'New')

    scheduled_date = fields.Datetime(string='Scheduled Date')
    subject = fields.Char(string='Subject')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    owner_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('follow_up', 'Follow_up'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='scheduled')
    description = fields.Text(string='Description')
    followup_date = fields.Date(string="Follow up Date")
    notes =  fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('follow.up')
                or 'New'
            )
        return super().create(vals)
    

  
    def action_done(self):
        for record in self:
            record.status = 'completed'


class CrmLead(models.Model):
    _inherit = 'crm.lead'
 
    follow_up_ids = fields.One2many(
        'follow.up',    
        'lead_id',       
        string="Follow Ups"
    )
    remarks = fields.Text(string="Remarks")
    visit_date = fields.Date(string="Visit Date")
    lead_type = fields.Selection([('fresh','Fresh'),('followup','followup')],string="Lead Type")
    site_visit_ids = fields.One2many('site.visit', 'lead_id')
    related_source_ids = fields.One2many('related.source', 'lead_id')

    @api.model
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)

        if lead.source_id:
            self.env['related.source'].create({
                'lead_id': lead.id,
                'source_id': lead.source_id.id,
                'submission_date': fields.Datetime.now(),
                'owner_id': lead.user_id.id or self.env.user.id,
                'lead_type': 'fresh',
                'status': 'new',
            })

        return lead

# RelatedSource
class RelatedSource(models.Model):
    _name = 'related.source'
    _description = 'Related Source'

    name = fields.Char(string="Related Source", required=True, readonly=True, copy=False, default='New')
    lead_type = fields.Selection([
        ('fresh', 'Fresh'),
        ('follow_up', 'Follow Up')
    ], string="Lead Type", default='fresh')
    submission_date = fields.Datetime(string="Submission Date")
    lead_id = fields.Many2one('crm.lead', string="Lead")
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('Completed', 'Completed')
    ], string="Status", default='new')
    owner_id = fields.Many2one('res.users', 
                               string="Owner", default=lambda self: self.env.user)
    


    source_id = fields.Many2one(
        'utm.source',
        string="Source",
        help="The source from which this related source originated"
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('related.source') or 'New'
        return super(RelatedSource, self).create(vals)
    
     
# site visit
class SiteVisit(models.Model):
    _name = 'site.visit'
    _description = 'Site Visit'
    _rec_name = 'site_visit_number'

    site_visit_number = fields.Char(
        string="Site Visit Number", 
        required=True, 
        copy=False, 
        readonly=True, 
        default='New'
    )
    visit_date = fields.Date(string="Visit Date")
    name = fields.Char(string="Site Visit ID")
    remarks = fields.Text(string="Remarks")
    
    lead_id = fields.Many2one(
        'crm.lead', 
        string="Lead", 
        ondelete='set null'
    )
    scheduled_date = fields.Datetime(string="Scheduled Date")
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string="Status", default='scheduled')
    source = fields.Selection([
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('other', 'Other')
    ], string="Source")
    canceled_reason = fields.Text(string="Canceled Reason")
    reschedule_date = fields.Datetime(string="Reschedule Date")

    owner_id = fields.Many2one(
        'res.users', 
        string="Owner", 
        ondelete='set null'
    )
    project_id = fields.Many2one(
        'project.project', 
        string="Project", 
        ondelete='set null'
    )
    feedback = fields.Text(string="Feedback")
    visit_type = fields.Selection([
        ('fresh', 'Fresh'),
        ('follow_up', 'Follow Up')
    ], string="Visit Type")
    visit_notes = fields.Text(string="Visit Notes")

    @api.model
    def create(self, vals):
        if vals.get('site_visit_number', 'New') == 'New':
            vals['site_visit_number'] = self.env['ir.sequence'].next_by_code('site.visit') or 'New'
        return super(SiteVisit, self).create(vals)


    