from odoo import models, fields


class ModuleModule(models.Model):
    _name = 'cus.module'

    name = fields.Char(string="Status Name", required=True)
    description = fields.Text(string="Description")
