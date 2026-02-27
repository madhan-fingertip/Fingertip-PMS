import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CustomEnquiryAPI(http.Controller):
    """
    Standalone JSON API: POST /custom/contactus
    Accepts JSON body and creates x.enquiry record directly.
    Used by external systems (mobile apps, websites, etc.)
    """

    @http.route('/custom/contactus', type='json', auth='public',
                methods=['POST'], csrf=False)
    def custom_contactus(self, **kwargs):
        name    = (kwargs.get('name') or '').strip()
        phone   = (kwargs.get('phone') or '').strip()
        email   = (kwargs.get('email') or '').strip()
        company = (kwargs.get('company') or '').strip()
        subject = (kwargs.get('subject') or '').strip()
        message = (kwargs.get('message') or '').strip()

        if not name:
            return {'status': 'error', 'message': 'Name is required.'}
        if not email:
            return {'status': 'error', 'message': 'Email is required.'}
        if not subject:
            subject = 'Contact Us Enquiry'
        if not message:
            message = '(no message)'

        record = request.env['x.enquiry'].sudo().create({
            'x_name'   : name,
            'x_phone'  : phone,
            'x_email'  : email,
            'x_company': company,
            'x_subject': subject,
            'x_message': message,
        })

        _logger.info(
            "x.enquiry created via API: ID=%s name=%s email=%s",
            record.id, name, email,
        )

        return {
            'status' : 'success',
            'message': 'Enquiry submitted successfully.',
            'id'     : record.id,
        }


# Override the Odoo website form controller to intercept Contact Us submissions
try:
    from odoo.addons.website.controllers.form import WebsiteForm

    class CustomWebsiteForm(WebsiteForm):
        """
        Override WebsiteForm to intercept Contact Us form submissions.
        When the form targets 'crm.lead', save into x.enquiry instead.
        """

        @http.route('/website/form/<string:model_name>', type='http',
                    auth='public', methods=['POST'], website=True, csrf=False)
        def website_form(self, model_name, **kwargs):
            if model_name == 'crm.lead':
                try:
                    name    = (kwargs.get('contact_name') or kwargs.get('name') or '').strip()
                    phone   = (kwargs.get('phone') or '').strip()
                    email   = (kwargs.get('email_from') or kwargs.get('email') or '').strip()
                    company = (kwargs.get('partner_name') or kwargs.get('company') or '').strip()
                    subject = (kwargs.get('subject') or 'Contact Us Enquiry').strip()
                    message = (kwargs.get('description') or kwargs.get('message') or '').strip()

                    if not name:
                        name = 'Website Visitor'
                    if not email:
                        email = 'unknown@unknown.com'
                    if not message:
                        message = '(no message provided)'

                    record = request.env['x.enquiry'].sudo().create({
                        'x_name'   : name,
                        'x_phone'  : phone,
                        'x_email'  : email,
                        'x_company': company,
                        'x_subject': subject,
                        'x_message': message,
                    })

                    _logger.info(
                        "x.enquiry created from website Contact Us form: ID=%s name=%s email=%s",
                        record.id, name, email,
                    )

                    return request.make_response(
                        json.dumps({'id': record.id}),
                        headers=[('Content-Type', 'application/json')],
                    )

                except Exception as e:
                    _logger.error("Failed to create x.enquiry from website form: %s", e)
                    return super().website_form(model_name, **kwargs)

            return super().website_form(model_name, **kwargs)

except ImportError:
    _logger.warning(
        "custom_enquiry: Could not import WebsiteForm — "
        "website form override not active. Only /custom/contactus API is available."
    )