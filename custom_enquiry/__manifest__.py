{
    'name': 'Custom Enquiry',
    'version': '18.0.1.0.0',
    'summary': 'Store website contact form submissions in custom model',
    'author': 'Fingertip',
    'depends': ['base', 'website'],
    'data': [
        'views/enquiry_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}