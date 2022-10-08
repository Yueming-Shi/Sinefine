# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateTransportWizard(models.TransientModel):
    _name = 'shipping.bill.update.transport.wizard'

    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            _datas = data.split('\t')
            if len(_datas) != 3:
                raise UserError(f'第{i+1}次 数据异常')
            name, logistics, tracking_no = _datas
            name, logistics, tracking_no = name.strip(), logistics.strip(), tracking_no.strip()
            shipping_bill = self.env['shipping.bill'].search([('name','=',name),('state','=','valued')],limit=1)

            shipping_bill.write({
                'out_date': _today,
                'logistics': logistics,
                'tracking_no': tracking_no,
                'state': 'transported',
            })
