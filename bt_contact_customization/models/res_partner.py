from odoo import models, fields,api

class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    account_status_id = fields.Many2one('res.partner.account.status', string="Account Status")

    rating = fields.Selection([
        ('hot', 'Hot'),
        ('cold', 'Cold'),
        ('warm', 'Warm'),

    ], string="Rating")

    #activity_count_custom = fields.Integer(string="Activity Count")
    activity_count_custom = fields.Integer(string="Activity Count",compute="_compute_activity_count_custom")

    @api.depends('activity_ids')
    def _compute_activity_count_custom(self):
        Activity = self.env['mail.activity']

        for partner in self:
            domain = [
                    ('res_model', '=', partner._name),
                    ('res_id', 'in', partner.ids),
                    ('active', 'in', [True, False]),
                ]
            partner.activity_count_custom =  Activity.search_count(domain)
    annual_revenue = fields.Integer(string="Annual Revenue")
    annual_revenue_range = fields.Char(string="Annual Revenue Range")
    company_linkedin = fields.Char(string="Company LinkedIn")
    contact_date = fields.Date(string="Contact Date")
    # description = fields.Text(string="Description")
    duplicate_check = fields.Boolean(string="Duplicate")
    company_eid = fields.Char(string="EID")
    employees = fields.Many2one('res.users',string="Employee")

    first_activity_datetime = fields.Datetime(
        compute='_compute_activity_dates',
        store=True,
        index=True
    )

    last_activity_datetime = fields.Datetime(
        compute='_compute_activity_dates',
        store=True,
        index=True
    )

    # ---------------------------------------------------------
    # Compute partner activity dates FROM mail.activity
    # ---------------------------------------------------------
    @api.depends(
        'activity_ids',  # fallback (chatter activities)
    )
    def _compute_activity_dates(self):
        Activity = self.env['mail.activity']

        for partner in self:
            if partner.is_company:
                domain = [
                    ('parent_partner_id', '=', partner.id),
                    ('active', 'in', [True, False]),
                ]
            else:
                domain = [
                    ('child_partner_id', '=', partner.id),
                    ('active', 'in', [True, False]),
                ]

            activities = Activity.search(domain, order='create_date asc')

            if activities:
                partner.first_activity_datetime = activities[0].create_date
                partner.last_activity_datetime = activities[-1].create_date
            else:
                partner.first_activity_datetime = False
                partner.last_activity_datetime = False

    pain_points = fields.Text(string="Pain Points")
    source_id = fields.Many2one('utm.source', string="Source")
    sub_vertical = fields.Char(string="Sub Vertical")
    working_date = fields.Date(string="Working Date")
    email_1 = fields.Char(string="Email 1")
    email_2 = fields.Char(string="Email 2")
    mobile_1 = fields.Char(string="Mobile 1")
    contact_eid = fields.Char(string="EID")
    contact_linkedin = fields.Char(string="LinkedIn")
    contact_account = fields.Char(string="Account")
    company_domain = fields.Char(string="Company Domain")
    # department = fields.Many2one('res.partner.industry',string="Department")
    department = fields.Char(string="Department")

