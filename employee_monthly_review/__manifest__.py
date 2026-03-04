{
    "name": "Employee Monthly Review",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "security/employee_review_security.xml",
        "views/review_views.xml",
    ],
    'images': ['static/description/performance_review.png'],
    "installable": True,
    "application": True,
}
