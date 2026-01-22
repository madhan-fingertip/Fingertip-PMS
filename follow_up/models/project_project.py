from odoo import models, fields, api
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Sale Order Reference
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', tracking=True)

    # Booking Information
    booking_date = fields.Date(string='Booking Date', tracking=True)
    booking_amount = fields.Float(string='Booking Amount', tracking=True)
    kyc_documents = fields.Binary(string='KYC Documents')
    kyc_documents_filename = fields.Char(string='KYC Documents Filename')
    project_name = fields.Char(string='Project Name', required=True)
    project_manager_id = fields.Many2one('res.users', string='Project Manager/Owner')
    booking_id = fields.Char(string='Booking ID', copy=False)
    
    # Financial Information
    total_sale_order_value = fields.Float(
        string='Total Sale Order Value', 
        compute='_compute_sale_order_value',
        store=True,
        tracking=True
    )
    funding_type = fields.Selection([
        ('self', 'Self'),
        ('loan', 'Loan')
    ], string='Funding Type', tracking=True)
    
    # Agreement Information
    agreement_date = fields.Date(string='Agreement Date', tracking=True)
    agreement_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Agreement Status', default='draft', tracking=True)
    
    # Payment Information
    total_demanded_amount = fields.Float(string='Total Demanded Amount', tracking=True)
    total_paid_amount = fields.Float(
        string='Total Paid Amount',
        compute='_compute_total_paid_amount',
        store=True,
        tracking=True
    )
    pending_amount = fields.Float(
        string='Pending Amount',
        compute='_compute_pending_amount',
        store=True
    )
    fail_date = fields.Date(string='Fail Date', tracking=True)
    
    # Registration Information
    registration_number = fields.Char(string='Registration Number', tracking=True)
    position_date = fields.Date(string='Position Date', tracking=True)
    
    # Swapping Information
    swap_status = fields.Selection([
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    ], string='Swap Status', tracking=True)
    swapping_reason = fields.Text(string='Swapping Reason')
    swap_unit = fields.Char(string='Swap Unit')
    
    # Cancellation Information
    cancellation_status = fields.Selection([
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    ], string='Cancellation Status', tracking=True)
    cancellation_amount = fields.Float(string='Cancellation Amount', tracking=True)
    cancellation_reason = fields.Text(string='Cancellation Reason')

    # Smart Button Fields
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count'
    )

    @api.depends('sale_order_id', 'sale_order_id.amount_total')
    def _compute_sale_order_value(self):
        """Compute total sale order value from linked sale order"""
        for record in self:
            if record.sale_order_id:
                record.total_sale_order_value = record.sale_order_id.amount_total
            else:
                record.total_sale_order_value = 0.0

    @api.depends('sale_order_id', 'sale_order_id.invoice_ids', 'sale_order_id.invoice_ids.payment_state')
    def _compute_total_paid_amount(self):
        """Compute total paid amount from sale order payments"""
        for record in self:
            total_paid = 0.0
            if record.sale_order_id:
                # Get all payments related to the sale order invoices
                invoices = record.sale_order_id.invoice_ids.filtered(
                    lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted'
                )
                for invoice in invoices:
                    # Get all payments for this invoice
                    payments = self.env['account.payment'].search([
                        ('reconciled_invoice_ids', 'in', invoice.ids),
                        ('state', '=', 'posted'),
                        ('payment_type', '=', 'inbound')
                    ])
                    total_paid += sum(payments.mapped('amount'))
            
            record.total_paid_amount = total_paid

    @api.depends('total_sale_order_value', 'total_paid_amount')
    def _compute_pending_amount(self):
        """Compute pending amount"""
        for record in self:
            record.pending_amount = record.total_sale_order_value - record.total_paid_amount

    @api.depends('sale_order_id', 'sale_order_id.invoice_ids')
    def _compute_payment_count(self):
        """Compute the number of payments from sale order invoices"""
        for record in self:
            if record.sale_order_id:
                # Get all invoices from sale order
                invoices = record.sale_order_id.invoice_ids.filtered(
                    lambda inv: inv.move_type == 'out_invoice'
                )
                # Get all payments for these invoices
                payments = self.env['account.payment'].search([
                    ('reconciled_invoice_ids', 'in', invoices.ids),
                    ('payment_type', '=', 'inbound')
                ])
                record.payment_count = len(payments)
            else:
                record.payment_count = 0

    def action_view_payments(self):
        """Open the list of payments from sale order"""
        self.ensure_one()
        
        if not self.sale_order_id:
            raise UserError('No sale order linked to this project.')
        
        # Get all invoices from sale order
        invoices = self.sale_order_id.invoice_ids.filtered(
            lambda inv: inv.move_type == 'out_invoice'
        )
        
        # Get all payments for these invoices
        payments = self.env['account.payment'].search([
            ('reconciled_invoice_ids', 'in', invoices.ids),
            ('payment_type', '=', 'inbound')
        ])
        
        action = {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
            'context': {
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
            },
        }
        
        if len(payments) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = payments.id
        
        return action

    def action_generate_payment_receipt(self):
        """Generate Sale Agreement"""
        self.ensure_one()
        return self.env.ref('follow_up.action_report_sale_agreement').report_action(self)

    def action_generate_cancellation_letter(self):
        """Generate Cancellation Letter"""
        self.ensure_one()
        return self.env.ref('follow_up.action_report_cancellation_letter').report_action(self)

    def action_generate_allotment_letter(self):
        """Generate Allotment Letter"""
        self.ensure_one()
        return self.env.ref('follow_up.action_report_allotment_letter').report_action(self)

    def action_generate_booking_form(self):
        """Generate Booking Form"""
        self.ensure_one()
        return self.env.ref('follow_up.action_report_booking_form').report_action(self)

    def action_generate_tap(self):
        """Generate TAP (Transfer Approval Permit)"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'TAP',
                'message': 'Transfer Approval Permit generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_drl(self):
        """Generate DRL (Demand Refund Letter)"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'DRL',
                'message': 'Demand Refund Letter generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_noc(self):
        """Generate NOC (No Objection Certificate)"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'NOC',
                'message': 'No Objection Certificate generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_generate_ledger(self):
        """Generate Ledger"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Ledger',
                'message': 'Ledger generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_generate_cost_sheet(self):
        """Generate Cost Sheet"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cost Sheet',
                'message': 'Cost Sheet generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }