from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_round


class HrVersion(models.Model):
    _inherit = 'hr.version'

    net_wage = fields.Monetary(
        string="Net (Take Home)", compute='_compute_net_wage', inverse='_inverse_net_wage',
        groups="hr_payroll.group_hr_payroll_user",
        help="Take-home pay of a full month at this wage, computed with the salary structure. "
             "Enter an amount to back-calculate the wage.")

    @api.depends('wage', 'structure_type_id', 'employee_id', 'company_id')
    def _compute_net_wage(self):
        for version in self:
            version.net_wage = version._get_net_for_wage(version.wage) if version.wage else 0.0

    def _inverse_net_wage(self):
        for version in self:
            if not version.net_wage:
                continue
            # Already giving this net (e.g. the form sends back the computed value): keep the wage.
            if version.currency_id.is_zero(version._get_net_for_wage(version.wage) - version.net_wage):
                continue
            version.wage = version._get_wage_for_net(version.net_wage)

    @api.onchange('net_wage')
    def _onchange_net_wage(self):
        if self.net_wage:
            self.wage = self._get_wage_for_net(self.net_wage)

    def _get_net_for_wage(self, wage):
        """ Take-home pay (sum of the Net category rules) of a full month at ``wage``. """
        self.ensure_one()
        struct = self.structure_type_id.default_struct_id
        if not struct or not self.employee_id:
            return 0.0
        payslip = self.env['hr.payslip'].with_context(
            salary_simulation=True,
            net_to_wage_simulated_wage=wage,
            prevent_payslip_computation_line_ids=struct.rule_ids.filtered('exclude_from_net_wage').ids,
        ).new({
            'name': 'Net to Wage Simulation',
            'employee_id': self.employee_id.id,
            'version_id': self.id,
            'struct_id': struct.id,
            'company_id': (self.company_id or self.employee_id.company_id).id,
            'date_from': fields.Date.today().replace(day=1),
            'worked_days_line_ids': [],
            'input_line_ids': [],
        })
        net_rule_ids = struct.rule_ids.filtered(lambda rule: rule.category_id.code == 'NET').ids
        return sum(line['total'] for line in payslip._get_payslip_lines()
                   if line['salary_rule_id'] in net_rule_ids)

    def _get_wage_for_net(self, net):
        """ Smallest wage (in currency units) whose take-home pay reaches ``net``. """
        self.ensure_one()
        if not self.structure_type_id.default_struct_id:
            raise UserError(self.env._("Set a salary structure type before entering a net amount."))
        low, high = 0.0, max(net, 1.0)
        while self._get_net_for_wage(high) < net:
            if high > net * 1000 + 1e9:
                raise UserError(self.env._(
                    "No wage gives a take-home pay of %(net)s with this salary structure.", net=net))
            low, high = high, high * 2
        rounding = self.currency_id.rounding or 0.01
        while high - low > rounding / 2:
            middle = (low + high) / 2
            if self._get_net_for_wage(middle) < net:
                low = middle
            else:
                high = middle
        wage = float_round(high, precision_rounding=rounding, rounding_method='DOWN')
        if self.currency_id.compare_amounts(self._get_net_for_wage(wage), net) < 0:
            wage += rounding
        return wage
