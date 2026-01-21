{
    'name': 'Project Customization',
    'version': '18.0.1.0.1',
    'description': 'Project Customization.',
    'category': 'Project',
    'author': 'Broadtech',
    'depends': ['project','hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/project_timesheet_group.xml',
        'views/project_project_views.xml',
        'views/project_milestone_views.xml',
        'views/project_task_views.xml',
        'views/module_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
