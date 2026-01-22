# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        """Override create to set default values when creating from lead"""
        res = super(SaleOrder, self).create(vals)
        if res.opportunity_id:
            for line in res.order_line:
                line._set_default_project_values()
        
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _set_default_project_values(self):
        """Set default project-related values on order line"""
        self.ensure_one()
        
        if self.product_id:
            if self.product_id.type != 'service':
                self.product_id.write({'type': 'service'})
            self.product_id.write({
                'service_tracking': 'project_only',
            })
            project_template = self.env['project.project'].search([
                ('name', '=', 'project template'),
            ], limit=1)
            if project_template:
                self.product_id.write({
                    'project_template_id': project_template.id,
                })
            self.product_id.write({
                'service_policy': 'delivered_milestones',
            })
            uom_unit = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
            if uom_unit:
                self.product_id.write({
                    'uom_id': uom_unit.id,
                    'uom_po_id': uom_unit.id,
                })

    @api.model
    def create(self, vals):
        """Override create to apply defaults when line is created"""
        res = super(SaleOrderLine, self).create(vals)
        if res.order_id.opportunity_id and res.product_id:
            res._set_default_project_values()
        
        return res


class SaleOrderLineDefaults(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, fields_list):
        """Set default values for new order lines from leads"""
        res = super(SaleOrderLineDefaults, self).default_get(fields_list)
        if self.env.context.get('default_order_id'):
            order = self.env['sale.order'].browse(self.env.context['default_order_id'])
            if order.opportunity_id:
                uom_unit = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
                if uom_unit:
                    res['product_uom'] = uom_unit.id
        
        return res