# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateDiscardWizard(models.TransientModel):
    _name = 'shipping.bill.update.discard.wizard'
    
    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            _datas = data.split('\t')
            if len(_datas) != 1:
                raise UserError(f'第{i+1}次 数据异常')
            name = _datas[0]
            name = name.strip()

            shipping_bill = self.env['shipping.bill'].search([('name','=',name),],limit=1)

            if not shipping_bill:
                raise UserError(f'未找到 {name} 的单据')
            shipping_bill.write({
                'discarded_date': _today,
                'state': 'discarded',
            })
