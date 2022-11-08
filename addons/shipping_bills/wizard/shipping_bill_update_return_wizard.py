# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateReturnWizard(models.TransientModel):
    _name = 'shipping.bill.update.return.wizard'
    
    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            _datas = data.split('\t')
            if len(_datas) != 2:
                raise UserError(f'第{i+1}次 数据异常')
#            name, return_address, return_contact, return_mobile, return_name = _datas
#            name, return_address, return_contact, return_mobile, return_name = name.strip(),\
#                    return_address.strip(), return_contact.strip(), return_mobile.strip(),\
#                     return_name.strip(),  
            
            name, return_name = _datas
            name, return_name = name.strip(), return_name.strip(),  

            shipping_bill = self.env['shipping.bill'].search(['|',('name','=',name),('picking_code','=',name),('state','=','valued')],limit=1)

            if not shipping_bill:
                raise UserError(f'未找到 {name} 的单据')
            shipping_bill.write({
                'returned_date': _today,
                'state': 'returned',
#                'return_address': return_address,
#                'return_contact': return_contact,
#                'return_mobile': return_mobile,
                'return_name': return_name,
            })
