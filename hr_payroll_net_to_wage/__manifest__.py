{
    'name': 'Payroll: Net to Wage',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': "Enter the take-home pay and get the wage that produces it",
    'description': """
Adds a "Net (Take Home)" field next to the wage of an employee. It shows the take-home pay
the current wage gives, computed with the employee's own salary structure (the rules of
category Net). Typing a net amount back-calculates the wage that produces it.

Salary rules flagged "Ignore in Net to Wage" (e.g. one-off salary advances) are left out
of the calculation.
""",
    'author': 'OdooHandyModules',
    'license': 'LGPL-3',
    'depends': ['hr_payroll'],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_salary_rule_views.xml',
    ],
    'installable': True,
    'application': False,
}
