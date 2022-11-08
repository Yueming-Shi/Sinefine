# See LICENSE file for full copyright and licensing details.
import requests
import json

from odoo import api
from odoo import models
from odoo.exceptions import UserError

odoo_session = requests.Session()


class ShippingBill(models.Model):
    _inherit = 'shipping.bill'

    def write(selfs, vals):
        result = super().write(vals)
        for self in selfs:
            openid = self.sale_partner_id.user_ids.wx_openid
            # 获取token
            token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
            data = {}
            if openid:
                if vals.get('state') == 'returned':
                    data = {
                        "touser": openid,
                        "template_id": "3yfETXzY9V-3xPLWlxOGc7ItkNWPLCyusqKaLQkQgDI",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "尊敬的客户" + ' ' + self.sale_partner_id.name + ',' + '您的包裹已退运。',
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": self.name,
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.shipping_factor_id.name,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": "订单已退运",
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "退运快递单号：" + self.name,
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
                elif vals.get('state') == 'transported':
                    if self.picking_code:
                        code = self.picking_code
                    else:
                        code = ''
                    data = {
                        "touser": openid,
                        "template_id": "K61LcyZbCm8ge3hsrPkr20EAOjsH6ZkKumOSERi9qPo",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "您好，您的包裹已发货，取件码：" + code + '。',
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": self.name,
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.logistics,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": self.tracking_no,
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "点击查看详情。",
                                "color": "#173177"
                            },
                        },
                    }
                    # 给站点人发邮件
                    name = self.name or ''
                    logistics = self.logistics or ''
                    tracking_no = self.tracking_no or ''
                    mail = self.env['mail.mail'].create({
                        'subject': '包裹已发到你的站点。',
                        'email_from': 'info@sinefine.store',
                        'email_to': self.sale_site_id.email,
                        'body_html': '<p>运单号：' + name + '</p>' + '<p>物流商：' + logistics + '</p>' + '<p>物流追踪码：' + tracking_no + '</p>'
                    })
                    mail.send()

                    self.wx_information_send(token, data)
                elif vals.get('state') == 'arrived':
                    data = {
                        "touser": openid,
                        "template_id": "39cHpuIfpSc6Vi_iclQ1Mg2skCg_-jC3nFNnuVXK4A4",
                        "url": "",
                        "miniprogram": {},
                        "client_msg_id": "",
                        "data": {
                            "first": {
                                "value": "您好，您的包裹已到站。",
                                "color": "#173177"
                            },
                            "keyword1": {
                                "value": self.sale_site_id.name,
                                "color": "#173177"
                            },
                            "keyword2": {
                                "value": self.picking_code,
                                "color": "#173177"
                            },
                            "keyword3": {
                                "value": self.sale_partner_id.name,
                                "color": "#173177"
                            },
                            "keyword4": {
                                "value": self.sale_invoice_ids[0].amount_total,
                                "color": "#173177"
                            },
                            "remark": {
                                "value": "点击查看详情。",
                                "color": "#173177"
                            },
                        },
                    }
                    self.wx_information_send(token, data)
        return result

    def multi_action_compute(selfs):
        result = super().multi_action_compute()
        for self in selfs:
            openid = self.sale_partner_id.user_ids.wx_openid
            # 获取token
            token = selfs.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
            data = {
                "touser": openid,
                "template_id": "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
                "url": "https://trans.sinefine.store/order/trans/unpaid",
                "miniprogram": {},
                "client_msg_id": "",
                "data": {
                    "first": {
                        "value": "您好，您的包裹已到达仓库。",
                        "color": "#173177"
                    },
                    "orderno": {
                        "value": self.name,
                        "color": "#173177"
                    },
                    "amount": {
                        "value": str('{0:,.2f}'.format(self.fee)),
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "请在72小时内完成支付，避免延误发货。",
                        "color": "#173177"
                    },
                },
            }
            self.wx_information_send(token, data)
        return result

    def wx_information_send(self, token, data):
        send_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % token

        headers = {
            'Content-Type': 'application/json'
        }
        data_json = json.dumps(data)

        odoo_session.post(url=send_url, data=bytes(data_json, 'utf-8'), headers=headers)

        return True
