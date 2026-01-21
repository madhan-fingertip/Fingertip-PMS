from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    estimated = fields.Float(string='Estimated')
    actual = fields.Float(string='Actual')
    module_id = fields.Many2one('cus.module',string="Module")
    wc_id = fields.Char(string='Wc Id')
