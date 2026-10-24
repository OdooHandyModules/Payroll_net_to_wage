from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_contract_wage(self):
        if 'net_to_wage_simulated_wage' in self.env.context:
            return self.env.context['net_to_wage_simulated_wage']
        return super()._get_contract_wage()
