# -*- coding: utf-8 -*-
import werkzeug.urls
from urllib.parse import urlparse
import urllib.request
import json

from odoo import api, fields, models
from odoo.tools.misc import ustr
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_oauth.controllers.main import OAuthLogin

class ResUsers(models.Model):
    _inherit = 'res.users'

    wx_openid = fields.Char(string='微信OpenID', help="用于微信公众号授权登录Odoo", copy=False)

    @api.model
    def wx_auth(self, openid):
        user_id = self.search([('wx_openid', '=', openid)], limit=1)
        if not user_id:
            raise AccessDenied("微信访问用户【openid：%s】没有关联系统账号！" % (openid, ))

        return (self.env.cr.dbname, user_id.login, openid)

    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            passwd_allowed = env['interactive'] or not self.env.user._rpc_api_keys_only()
            if passwd_allowed and self.env.user.active:
                res = self.sudo().search([('id', '=', self.env.uid), ('wx_openid', '=', password)])
                if res:
                    return
            raise
