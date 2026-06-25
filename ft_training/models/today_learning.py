from odoo import models, fields, _


class TodayLearning(models.Model):
    _name = 'ft.today.learning'
    _description = "Today's Learning"
    _order = 'create_date desc'
    _rec_name = 'learning_topic_id'

    learning_topic_id = fields.Many2one(
        'ft.learning.topic', string='Learning Topic', required=True,
        ondelete='restrict',
    )
    description = fields.Html(
        string='Description',
        help='What you learned. Rich text — supports formatting and images.',
    )
    # No manual date field: the system Created Date is used instead.
    # create_date / create_uid are provided automatically by Odoo.

    def name_get(self):
        result = []
        for rec in self:
            topic = rec.learning_topic_id.name or _("Learning")
            day = fields.Date.to_string(rec.create_date) if rec.create_date else ''
            result.append((rec.id, f"{topic} ({day})" if day else topic))
        return result
