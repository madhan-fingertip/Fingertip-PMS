from odoo import models, fields, api


class ProjectActivityUpdate(models.Model):
    _name = 'project.activity.update'
    _description = 'Project Activity Update'
    _order = 'update_date desc, id desc'

    name = fields.Char(string='Today Update', required=True)
    update_date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade'
    )
    project_manager_id = fields.Many2one(
        'res.users',
        string='Project Manager',
        related='project_id.user_id',
        store=True,
        readonly=True
    )
    
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.name} - {rec.update_date}"
            result.append((rec.id, name))
        return result