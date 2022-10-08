# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wechat_appid = fields.Char("AppID", config_parameter='wechat.appid', default='')
    wechat_appsecret = fields.Char("Appsecret", config_parameter='wechat.appsecret', default='')
    wechat_token = fields.Char("Token", config_parameter='wechat.token', default='')
