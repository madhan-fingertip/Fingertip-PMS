# -*- coding: utf-8 -*-
from odoo import fields, models


class MarketingArticle(models.Model):
    _name = "marketing.article"
    _description = "Marketing Article"
    _rec_name = "subject"
    _order = "create_date desc"

    industry = fields.Selection(
        selection=[
            ("real_estate", "Real Estate"),
            ("manufacturing", "Manufacturing"),
            ("consumer_goods", "Consumer Goods"),
            ("nbfc", "NBFC"),
            ("healthcare", "Healthcare"),
            ("hi_tech", "Hi Tech"),
            ("education", "Education"),
            ("agriculture", "Agriculture"),
        ],
        required=True,
        index=True,
    )

    technology = fields.Selection(
        selection=[
            ("salesforce", "Salesforce"),
            ("odoo", "Odoo"),
            ("web", "Web"),
            ("mobile", "Mobile"),
            ("ai", "AI"),
            ("ml", "ML"),
            ("website", "Website"),
        ],
        required=True,
        index=True,
    )

    type = fields.Selection(
        selection=[
            ("blog", "Blog"),
            ("work", "Work"),
        ],
        required=True,
        default="blog",
        index=True,
    )

    site = fields.Selection(
        selection=[
            ("fingertip", "Fingertip"),
            ("symake", "Symake"),
            ("bussus", "Bussus"),
        ],
        required=True,
        default="fingertip",
        index=True,
    )

    subject = fields.Char(required=True, index=True)
    image_url = fields.Char(string="Image URL")
    body_html = fields.Html(string="Body", sanitize=True)

    active = fields.Boolean(default=True)
    published_on = fields.Datetime(string="Published On")
