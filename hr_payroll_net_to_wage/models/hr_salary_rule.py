from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    exclude_from_net_wage = fields.Boolean(
        string="Ignore in Net to Wage",
        help="Leave this rule out when computing the take-home pay of a wage, "
             "e.g. one-off deductions such as salary advances.")
