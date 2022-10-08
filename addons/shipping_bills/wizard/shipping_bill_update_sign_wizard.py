# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateSignWizard(models.TransientModel):
    _name = 'shipping.bill.update.sign.wizard'

    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            input = data.strip()
            shipping_bill = self.env['shipping.bill'].search([('name','=',input),('state','=','arrived')],limit=1)
            if not shipping_bill:
                shipping_bill = self.env['shipping.bill'].search([('sale_fetch_no', '=', input),
                                                                  ('state', '=', 'arrived')],limit=1)
            if not shipping_bill:
                raise UserError(f'未找到 {input} 的单据')
            shipping_bill.write({
                'signed_date': _today,
                'state': 'signed',
            })
