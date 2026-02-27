{
    'name': 'Custom Enquiry',
    'version': '18.0.1.0.0',
    'summary': 'Store website contact form submissions in custom model',
    'author': 'Fingertip',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/enquiry_views.xml',
    ],
    'installable': True,
    'application': False,
}