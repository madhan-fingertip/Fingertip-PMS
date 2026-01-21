{
    'name': 'Contact Customization',
    'version': '18.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Contact Customization',
    'author': 'Broadtech',
    'depends': ['base','utm','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/contact_account_status.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
