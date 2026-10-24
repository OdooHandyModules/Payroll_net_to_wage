# Payroll Net to Wage

An Odoo 19 (Enterprise) module that adds a **Net (Take Home)** field next to the wage of
an employee and back-calculates the wage that produces a given net.

## What this module does

- Shows the take-home pay of the current wage, computed with the employee's own salary
  structure (sum of the rules of category Net) on a simulated full-month payslip.
- Typing a net amount computes the wage that produces it (bisection on the real salary
  rules, rounded to the currency), so it keeps working when rules or tax brackets change.
- Salary rules flagged **Ignore in Net to Wage** (e.g. one-off salary advances) are left out.

## Requirements

Odoo **19.0** Enterprise (`hr_payroll`).

## License

LGPL-3.
