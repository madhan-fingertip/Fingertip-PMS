from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class CustomContactUs(Website):

    # Override the default /contactus form submission
    @http.route(['/contactus'], type='http', auth='public', 
                methods=['POST'], website=True, csrf=True)
    def contactus_submit(self, **kwargs):
        """
        Override default Contact Us form submission.
        Saves data into x.enquiry custom model.
        """

        name    = kwargs.get('contact_name', '')
        phone   = kwargs.get('phone', '')
        email   = kwargs.get('email_from', '')
        company = kwargs.get('partner_name', '')
        subject = kwargs.get('subject', '')
        message = kwargs.get('description', '')

        # Save into custom x.enquiry model
        if name and email and subject and message:
            request.env['x.enquiry'].sudo().create({
                'x_name'   : name,
                'x_phone'  : phone,
                'x_email'  : email,
                'x_company': company,
                'x_subject': subject,
                'x_message': message,
            })

        # Redirect to thank you page after submission
        return request.redirect('/contactus?success=1')