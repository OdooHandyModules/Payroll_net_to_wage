from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    net_wage = fields.Monetary(
        related='version_id.net_wage', readonly=False, inherited=True,
        groups="hr_payroll.group_hr_payroll_user")

    @api.onchange('net_wage')
    def _onchange_net_wage(self):
        if self.net_wage:
            self.wage = self.version_id._get_wage_for_net(self.net_wage)
