# -*- coding: utf-8 -*-
# Part of Odoo.

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscalyear_last_day = fields.Integer(related='company_id.fiscalyear_last_day', required=True, readonly=False)
    fiscalyear_last_month = fields.Selection(related='company_id.fiscalyear_last_month', required=True, readonly=False)
    period_lock_date = fields.Date(string='Lock Date for Non-Advisers',
                                   related='company_id.period_lock_date', readonly=False)
    fiscalyear_lock_date = fields.Date(string='Lock Date for All Users',
                                       related='company_id.fiscalyear_lock_date', readonly=False)
    tax_lock_date = fields.Date("Tax Lock Date", related='company_id.tax_lock_date', readonly=False)
    use_anglo_saxon = fields.Boolean(string='Anglo-Saxon Accounting', related='company_id.anglo_saxon_accounting', readonly=False)
    module_account_predictive_bills = fields.Boolean(string="Account Predictive Bills")
    invoicing_switch_threshold = fields.Date(string="Invoicing Switch Threshold", related='company_id.invoicing_switch_threshold', readonly=False)
    group_fiscal_year = fields.Boolean(string='Fiscal Years', implied_group='account_accountant.group_fiscal_year')

    @api.constrains('fiscalyear_last_day', 'fiscalyear_last_month')
    def _check_fiscalyear(self):
        # We try if the date exists in 2020, which is a leap year.
        # We do not define the constrain on res.company, since the recomputation of the related
        # fields is done one field at a time.
        for wiz in self:
            try:
                date(2020, int(wiz.fiscalyear_last_month), wiz.fiscalyear_last_day)
            except ValueError:
                raise ValidationError(
                    _('Incorrect fiscal year date: day is out of range for month. Month: %s; Day: %s') %
                    (wiz.fiscalyear_last_month, wiz.fiscalyear_last_day)
                )

    @api.model
    def create(self, vals):
        # Amazing workaround: non-stored related fields on company are a BAD idea since the 2 fields
        # must follow the constraint '_check_fiscalyear_last_day'. The thing is, in case of related
        # fields, the inverse write is done one value at a time, and thus the constraint is verified
        # one value at a time... so it is likely to fail.
        self.env.company.write({
            'fiscalyear_last_day': vals.get('fiscalyear_last_day') or self.env.company.fiscalyear_last_day,
            'fiscalyear_last_month': vals.get('fiscalyear_last_month') or self.env.company.fiscalyear_last_month,
        })
        vals.pop('fiscalyear_last_day', None)
        vals.pop('fiscalyear_last_month', None)
        return super().create(vals)
