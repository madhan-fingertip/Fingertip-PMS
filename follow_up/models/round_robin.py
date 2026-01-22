from odoo import models, fields, api


class RoundRobin(models.Model):
    _name = 'round.robin'
    _description = 'Round Robin Configuration'
    _rec_name = 'project_name'

    project_name = fields.Char(string='Project Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    member_ids = fields.One2many(
        'round.robin.member',
        'round_robin_id',
        string='Round Robin Members'
    )
    last_assigned_index = fields.Integer(string='Last Assigned Index', default=0)

    def name_get(self):
        """Custom display name"""
        result = []
        for record in self:
            name = record.project_name or f'Round Robin #{record.id}'
            if not record.active:
                name = f'[Inactive] {name}'
            result.append((record.id, name))
        return result
        
    def get_next_user(self, user_type):
        """Get next user in round robin sequence for given type"""
        self.ensure_one()
        active_members = self.member_ids.filtered(
            lambda m: m.active and m.user_type == user_type and m.user_id
        )
        
        if not active_members:
            return False
        
        current_index = self.last_assigned_index % len(active_members)
        next_user = active_members[current_index].user_id
        
        self.last_assigned_index = current_index + 1
        
        return next_user


class RoundRobinMember(models.Model):
    _name = 'round.robin.member'
    _description = 'Round Robin Member'
    _rec_name = 'user_id'

    round_robin_id = fields.Many2one(
        'round.robin',
        string='Round Robin',
        required=True,
        ondelete='cascade'
    )
    user_type = fields.Selection([
        ('sales', 'Sales'),
        ('crm', 'CRM'),
        ('telecaller', 'Telecaller')
    ], string='User Type', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    active = fields.Boolean(string='Active', default=True)


class SalesTeamExtended(models.Model):
    _name = 'sales.team.member'
    _description = 'Round Robin'

    team_id = fields.Many2one('crm.lead', string='Team', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    user_type = fields.Selection([
        ('sales', 'Sales'),
        ('crm', 'CRM'),
        ('telecaller', 'Telecaller')
    ], string='Type', required=True)
    active = fields.Boolean(string='Status', default=True)


class CrmLeadExtended(models.Model):
    _inherit = 'crm.lead'

    team_member_ids = fields.One2many(
        'sales.team.member',
        'team_id',
        string='Round Robin'
    )
    round_robin_id = fields.Many2one(
        'round.robin',
        string='Round Robin',
        help='Select Round Robin configuration for automatic assignment'
    )

    @api.model
    def create(self, vals):
        """Auto-assign users from Round Robin when lead is created"""
        lead = super(CrmLeadExtended, self).create(vals)
        
        if lead.round_robin_id and lead.round_robin_id.active:
            self._assign_round_robin_users(lead)
        
        return lead

    def _assign_round_robin_users(self, lead):
        """Assign users from Round Robin to lead"""
        round_robin = lead.round_robin_id
        
        for user_type in ['sales', 'crm', 'telecaller']:
            user = round_robin.get_next_user(user_type)
            if user:
                self.env['sales.team.member'].create({
                    'team_id': lead.id,
                    'user_id': user.id,
                    'user_type': user_type,
                    'active': True
                })