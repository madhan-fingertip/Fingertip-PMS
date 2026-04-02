import json
import logging
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

TICKET_STATES = [
    ('new', 'New'),
    ('open', 'In Progress'),
    ('pending_internal', 'Pending Internal'),
    ('pending_customer', 'Pending Customer'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
    ('cancelled', 'Cancelled'),
]

PRIORITY_SELECTION = [
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'High'),
    ('3', 'Urgent'),
]

CHANNEL_SELECTION = [
    ('portal', 'Portal'),
    ('email', 'Email'),
    ('internal', 'Internal'),
]


class HelpdeskTicket(models.Model):
    _name = 'ft.helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'priority desc, create_date desc'
    _rec_name = 'display_name'

    # =====================
    # Core Fields
    # =====================
    name = fields.Char(
        string='Subject', required=True, tracking=True, index='trigram',
    )
    ticket_no = fields.Char(
        string='Ticket Number', readonly=True, copy=False,
        default='New', index=True,
    )
    display_name = fields.Char(
        string='Display Name', compute='_compute_display_name', store=True,
    )
    description = fields.Html(
        string='Description', sanitize_style=True,
    )
    customer_id = fields.Many2one(
        'res.partner', string='Customer', required=True,
        tracking=True, index=True,
    )
    customer_email = fields.Char(
        string='Customer Email', related='customer_id.email',
        store=True, readonly=True,
    )
    customer_phone = fields.Char(
        string='Customer Phone', related='customer_id.phone',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
        required=True, index=True,
    )

    color = fields.Integer(string='Color Index')

    # =====================
    # Classification
    # =====================
    team_id = fields.Many2one(
        'ft.helpdesk.team', string='Team', tracking=True, index=True,
    )
    assigned_user_id = fields.Many2one(
        'res.users', string='Assignee', tracking=True, index=True,
        domain="[('share', '=', False)]",
    )
    priority = fields.Selection(
        PRIORITY_SELECTION, string='Priority',
        default='1', tracking=True, index=True,
    )
    state = fields.Selection(
        TICKET_STATES, string='Status',
        default='new', required=True, tracking=True, index=True,
        group_expand='_group_expand_states',
    )
    type_id = fields.Many2one(
        'ft.helpdesk.ticket.type', string='Type', tracking=True,
    )
    category_id = fields.Many2one(
        'ft.helpdesk.category', string='Category', tracking=True,
    )
    subcategory_id = fields.Many2one(
        'ft.helpdesk.subcategory', string='Subcategory',
        domain="[('category_id', '=', category_id)]",
    )
    project_id = fields.Many2one(
        'project.project', string='Project', tracking=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Related Product',
    )
    tag_ids = fields.Many2many(
        'ft.helpdesk.tag', 'ft_helpdesk_ticket_tag_rel',
        'ticket_id', 'tag_id', string='Tags',
    )
    channel = fields.Selection(
        CHANNEL_SELECTION, string='Channel',
        default='portal', tracking=True,
    )

    # =====================
    # Dynamic Fields
    # =====================
    fieldset_id = fields.Many2one(
        related='type_id.fieldset_id', string='Fieldset', readonly=True,
    )
    dynamic_field_ids = fields.One2many(
        related='fieldset_id.field_ids', string='Dynamic Field Definitions',
        readonly=True,
    )
    dynamic_values = fields.Json(
        string='Dynamic Values', default=dict,
        help='JSON storage for dynamic form values.',
    )

    # =====================
    # Resolution & Close
    # =====================
    close_reason_id = fields.Many2one(
        'ft.helpdesk.close.reason', string='Close Reason',
    )
    resolution_summary = fields.Text(string='Resolution Summary')

    # =====================
    # Timestamps
    # =====================
    first_response_at = fields.Datetime(
        string='First Response At', readonly=True, copy=False,
    )
    resolved_at = fields.Datetime(
        string='Resolved At', readonly=True, copy=False,
    )
    closed_at = fields.Datetime(
        string='Closed At', readonly=True, copy=False,
    )
    cancelled_at = fields.Datetime(
        string='Cancelled At', readonly=True, copy=False,
    )
    due_date = fields.Datetime(string='Due Date', tracking=True)

    # =====================
    # Escalation
    # =====================
    is_escalated = fields.Boolean(
        string='Escalated', default=False, tracking=True,
    )
    escalation_level = fields.Integer(
        string='Escalation Level', default=0,
    )

    # =====================
    # Computed / Display
    # =====================
    age_hours = fields.Float(
        string='Age (Hours)', compute='_compute_age_hours',
        help='Hours since ticket creation.',
    )
    is_overdue = fields.Boolean(
        string='Overdue', compute='_compute_is_overdue',
        search='_search_is_overdue',
    )
    state_color = fields.Char(
        string='State Color', compute='_compute_state_color',
    )
    last_customer_reply_at = fields.Datetime(
        string='Last Customer Reply', readonly=True, copy=False,
    )
    last_agent_reply_at = fields.Datetime(
        string='Last Agent Reply', readonly=True, copy=False,
    )
    message_count = fields.Integer(
        string='Messages', compute='_compute_message_count',
    )
    customer_message_ids = fields.One2many(
        'mail.message', 'res_id', string='Customer Messages',
        compute='_compute_split_messages',
    )
    agent_message_ids = fields.One2many(
        'mail.message', 'res_id', string='Internal / System Messages',
        compute='_compute_split_messages',
    )

    # =====================
    # Portal
    # =====================
    access_token = fields.Char(string='Access Token', copy=False)

    # =====================
    # Computes
    # =====================

    @api.depends('ticket_no', 'name')
    def _compute_display_name(self):
        for ticket in self:
            if ticket.ticket_no and ticket.ticket_no != 'New':
                ticket.display_name = '[%s] %s' % (ticket.ticket_no, ticket.name)
            else:
                ticket.display_name = ticket.name

    def _compute_age_hours(self):
        now = fields.Datetime.now()
        for ticket in self:
            if ticket.create_date:
                delta = now - ticket.create_date
                ticket.age_hours = delta.total_seconds() / 3600.0
            else:
                ticket.age_hours = 0.0

    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for ticket in self:
            ticket.is_overdue = (
                ticket.due_date and ticket.due_date < now
                and ticket.state not in ('resolved', 'closed', 'cancelled')
            )

    def _search_is_overdue(self, operator, value):
        now = fields.Datetime.now()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                ('due_date', '<', now),
                ('state', 'not in', ('resolved', 'closed', 'cancelled')),
            ]
        return [
            '|',
            ('due_date', '>=', now),
            ('due_date', '=', False),
        ]

    def _compute_state_color(self):
        color_map = {
            'new': '#6c757d',
            'open': '#0d6efd',
            'pending_customer': '#ffc107',
            'pending_internal': '#fd7e14',
            'resolved': '#198754',
            'closed': '#20c997',
            'cancelled': '#dc3545',
        }
        for ticket in self:
            ticket.state_color = color_map.get(ticket.state, '#6c757d')

    def _compute_message_count(self):
        for ticket in self:
            ticket.message_count = len(ticket.message_ids)

    def _compute_split_messages(self):
        for ticket in self:
            customer_msgs = self.env['mail.message']
            agent_msgs = self.env['mail.message']
            for msg in ticket.message_ids:
                if msg.message_type in ('comment', 'email') and msg.author_id == ticket.customer_id:
                    customer_msgs |= msg
                else:
                    agent_msgs |= msg
            ticket.customer_message_ids = customer_msgs
            ticket.agent_message_ids = agent_msgs

    @api.model
    def _group_expand_states(self, states, domain):
        return [key for key, _ in TICKET_STATES]

    # =====================
    # CRUD Overrides
    # =====================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ticket_no', 'New') == 'New':
                vals['ticket_no'] = self.env['ir.sequence'].next_by_code(
                    'ft.helpdesk.ticket') or 'New'
            # Auto-assign team from type
            if not vals.get('team_id') and vals.get('type_id'):
                ticket_type = self.env['ft.helpdesk.ticket.type'].browse(vals['type_id'])
                if ticket_type.default_team_id:
                    vals['team_id'] = ticket_type.default_team_id.id
        tickets = super().create(vals_list)
        for ticket in tickets:
            # Auto-assign via round robin
            if (ticket.team_id and not ticket.assigned_user_id
                    and ticket.team_id.auto_assign_mode == 'round_robin'):
                assignee = ticket.team_id._get_next_assignee()
                if assignee:
                    ticket.assigned_user_id = assignee
            # Subscribe customer as follower and send creation confirmation
            if ticket.customer_id:
                ticket.message_subscribe(partner_ids=ticket.customer_id.ids)
                template = self.env.ref(
                    'ft_helpdesk_core.mt_ticket_new_email_template',
                    raise_if_not_found=False,
                )
                if template and ticket.customer_id.email:
                    try:
                        ticket.message_post_with_source(
                            source_ref=template,
                            subtype_xmlid='ft_helpdesk_core.mt_ticket_new',
                        )
                    except Exception:
                        _logger.warning(
                            'Failed to send new-ticket email for ticket %s',
                            ticket.ticket_no, exc_info=True,
                        )
        return tickets

    def write(self, vals):
        result = super().write(vals)
        # Track state-change timestamps
        if vals.get('state') == 'resolved':
            now = fields.Datetime.now()
            for ticket in self:
                if not ticket.resolved_at:
                    ticket.resolved_at = now
        elif vals.get('state') == 'closed':
            now = fields.Datetime.now()
            for ticket in self:
                if not ticket.closed_at:
                    ticket.closed_at = now
                if not ticket.resolved_at:
                    ticket.resolved_at = now
        elif vals.get('state') == 'cancelled':
            now = fields.Datetime.now()
            for ticket in self:
                if not ticket.cancelled_at:
                    ticket.cancelled_at = now
        return result

    # =====================
    # Actions
    # =====================

    def action_assign_to_me(self):
        """Assign ticket to current user and set to open if new."""
        for ticket in self:
            vals = {'assigned_user_id': self.env.uid}
            if ticket.state == 'new':
                vals['state'] = 'open'
            ticket.write(vals)

    def action_set_state_open(self):
        self.write({'state': 'open'})

    def action_set_state_pending_customer(self):
        self.write({'state': 'pending_customer'})

    def action_set_state_pending_internal(self):
        self.write({'state': 'pending_internal'})

    def action_set_state_resolved(self):
        self.write({'state': 'resolved'})

    def action_open_close_wizard(self):
        """Open close ticket wizard."""
        return {
            'name': _('Close Ticket'),
            'type': 'ir.actions.act_window',
            'res_model': 'ft.helpdesk.ticket.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id,
                'default_is_cancel': False,
            },
        }

    def action_open_cancel_wizard(self):
        """Open cancel ticket wizard."""
        return {
            'name': _('Cancel Ticket'),
            'type': 'ir.actions.act_window',
            'res_model': 'ft.helpdesk.ticket.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id,
                'default_is_cancel': True,
            },
        }

    def action_reopen(self):
        """Reopen a resolved/closed ticket."""
        for ticket in self:
            if ticket.state in ('resolved', 'closed', 'cancelled'):
                ticket.write({
                    'state': 'open',
                    'resolved_at': False,
                    'closed_at': False,
                    'cancelled_at': False,
                    'close_reason_id': False,
                })

    def action_escalate(self):
        """Escalate the ticket."""
        for ticket in self:
            ticket.write({
                'is_escalated': True,
                'escalation_level': ticket.escalation_level + 1,
                'priority': '3',  # Set to urgent
            })
            escalated_to = ''
            if ticket.team_id and ticket.team_id.leader_user_id:
                escalated_to = ticket.team_id.leader_user_id.name
            ticket.message_post(
                body=_('Ticket escalated to level %s.%s') % (
                    ticket.escalation_level,
                    _(' Escalated to: %s') % escalated_to if escalated_to else '',
                ),
                subtype_xmlid='ft_helpdesk_core.mt_ticket_internal_note',
                message_type='notification',
            )
            # Notify team leader
            if ticket.team_id and ticket.team_id.leader_user_id:
                ticket.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=ticket.team_id.leader_user_id.id,
                    summary=_('Escalated Ticket: %s') % ticket.ticket_no,
                    note=_('Ticket %s has been escalated to level %s.') % (
                        ticket.ticket_no, ticket.escalation_level),
                )

    def action_request_info(self):
        """Move to pending_customer and prompt for a reply template."""
        self.write({'state': 'pending_customer'})

    # =====================
    # Mail Thread Overrides
    # =====================

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values:
            return self.env.ref('ft_helpdesk_core.mt_ticket_state_change')
        return super()._track_subtype(init_values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Override to track first response and customer replies."""
        message = super().message_post(**kwargs)
        # Determine if this is a public reply by an agent
        subtype_id = kwargs.get('subtype_id')
        subtype_xmlid = kwargs.get('subtype_xmlid')
        is_internal = False
        if subtype_xmlid == 'ft_helpdesk_core.mt_ticket_internal_note':
            is_internal = True
        elif subtype_id:
            subtype = self.env['mail.message.subtype'].browse(subtype_id)
            if subtype == self.env.ref('ft_helpdesk_core.mt_ticket_internal_note', raise_if_not_found=False):
                is_internal = True

        if not is_internal and message.author_id:
            now = fields.Datetime.now()
            for ticket in self:
                # Agent reply
                if message.author_id != ticket.customer_id:
                    if not ticket.first_response_at:
                        ticket.first_response_at = now
                    ticket.last_agent_reply_at = now
                # Customer reply
                elif message.author_id == ticket.customer_id:
                    ticket.last_customer_reply_at = now
                    # Auto-reopen if pending_customer
                    if ticket.state == 'pending_customer':
                        ticket.state = 'open'
        return message

    def _get_access_token(self):
        """Generate access token for portal sharing."""
        self.ensure_one()
        if not self.access_token:
            self.access_token = self.env['ir.config_parameter'].sudo()._generate_token()
        return self.access_token

    def _compute_access_url(self):
        super()._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/support/ticket/%s' % ticket.id

    # =====================
    # Bulk Actions
    # =====================

    def action_bulk_assign(self):
        """Open bulk assign wizard for selected tickets."""
        return {
            'name': _('Assign Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'ft.helpdesk.ticket.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_ids': [(6, 0, self.ids)],
            },
        }

    def action_bulk_close(self):
        """Open bulk close wizard for selected tickets."""
        return {
            'name': _('Close Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'ft.helpdesk.ticket.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_ids': [(6, 0, self.ids)],
                'default_is_cancel': False,
            },
        }
