# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
odoo_session = requests.Session()

class WechatTest(http.Controller):

    def obtain_public_template(self, token):
        url = 'https://api.weixin.qq.com/wxaapi/newtmpl/getcategory?access_token=%s' % token
        res = odoo_session.get(url=url)
        return res.text

    def obtain_user_template(self, token):
        url = 'https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token=%s' % token
        res = odoo_session.get(url=url)
        return res.text

    @http.route('/wechat/test', type="http", auth='public', csrf=False)
    def wx_test(self, **kwargs):
        openid = request.env.user.wx_openid
        # 获取token
        token = request.env['ir.config_parameter'].search([('key', '=', 'wechat.access_token')]).value

        # # 获取公共模板
        # public_template = self.obtain_public_template(token)

        # # 获取私有模板
        # user_template = self.obtain_user_template(token)

        # 发送消息
        send_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % token
        data = {
            "touser": "o0To05t7cA7KP8WXPhUL5zYGrZJY",
            "template_id": "nyb0HsFu4oVOyR712tQFurlpt27foVsRwIb9pDge3vA",
            "url": "https://trans.sinefine.store/order/trans/unpaid",
            "miniprogram": {},
            "client_msg_id": "MSG_000001",
            "data": {
                "first": {
                    "value": "您好，您的包裹已到达仓库。",
                    "color": "#173177"
                },
                "orderno": {
                    "value": '123',
                    "color": "#173177"
                },
                "amount": {
                    "value": '123',
                    "color": "#173177"
                },
                "remark": {
                    "value": "请在72小时内完成支付，否则订单将被取消。",
                    "color": "#173177"
                },
            },
        }
        headers = {
            'Content-Type': 'application/json'
        }
        data_json = json.dumps(data)

        res = odoo_session.post(url=send_url, data=bytes(data_json, 'utf-8'), headers=headers)

        return res.text