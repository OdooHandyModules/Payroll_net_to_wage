from odoo import Command
from odoo.tests import Form, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestNetToWage(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref('hr_payroll.group_hr_payroll_manager')
        structure_type = cls.env['hr.payroll.structure.type'].create({'name': 'Net to Wage Test'})

        def rule(sequence, code, category, python, **vals):
            return Command.create({
                'name': code, 'code': code, 'sequence': sequence,
                'category_id': cls.env.ref(f'hr_payroll.{category}').id,
                'amount_select': 'code', 'amount_python_compute': python, **vals,
            })

        cls.structure = cls.env['hr.payroll.structure'].create({
            'name': 'Net to Wage Test',
            'type_id': structure_type.id,
            'rule_ids': [
                rule(1, 'BASIC', 'BASIC', "result = payslip.paid_amount"),
                # progressive tax: 0% up to 1000, 20% above
                rule(10, 'TAX', 'DED', "result = max(categories['BASIC'] - 1000, 0) * 0.2"),
                rule(20, 'ADVANCE', 'DED', "result = 300", exclude_from_net_wage=True),
                rule(100, 'TAKE_HOME', 'NET', "result = categories['BASIC'] - categories['DED']"),
            ],
        })
        structure_type.default_struct_id = cls.structure
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Net to Wage Employee',
            'wage': 3000,
            'structure_type_id': structure_type.id,
        })

    def test_net_from_wage(self):
        # 3000 - 20% of 2000; the advance is ignored
        self.assertAlmostEqual(self.employee.net_wage, 2600)
        self.assertAlmostEqual(self.employee.version_id.net_wage, 2600)

    def test_write_net_sets_wage(self):
        self.employee.net_wage = 1800
        # 1800 = W - 0.2 * (W - 1000)  =>  W = 2000
        self.assertAlmostEqual(self.employee.wage, 2000, delta=0.01)
        self.assertAlmostEqual(self.employee.net_wage, 1800, delta=0.01)

    def test_net_below_tax_threshold(self):
        self.employee.version_id.net_wage = 800
        self.assertAlmostEqual(self.employee.wage, 800, delta=0.01)

    def test_form_onchange(self):
        with Form(self.employee) as form:
            form.net_wage = 4200
            # 4200 = W - 0.2 * (W - 1000)  =>  W = 5000
            self.assertAlmostEqual(form.wage, 5000, delta=0.01)
        self.assertAlmostEqual(self.employee.wage, 5000, delta=0.01)

    def test_unchanged_net_keeps_wage(self):
        self.employee.wage = 3001
        self.employee.net_wage = self.employee.net_wage
        self.assertEqual(self.employee.wage, 3001)
