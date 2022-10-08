# -*- coding: utf-8 -*-
import json
import requests
import werkzeug
import urllib.parse
import logging
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import BadRequest
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo import registry as registry_get
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect, SIGN_UP_REQUEST_PARAMS
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.replies import TextReply

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.update({'wx_openid'})
class AuthSignupWX(AuthSignupHome):
    def _prepare_signup_values(self, qcontext):
        values = super(AuthSignupWX, self)._prepare_signup_values(qcontext)
        if qcontext.get('wx_openid', None):
            values['wx_openid'] = qcontext.get('wx_openid')
        return values
    

class WechatBizMsg(http.Controller):

    @http.route('/wechat/bizmsg', type="http", auth='public', csrf=False)
    def wx_bizmsg(self, **kwargs):
        """微信公众号消息处理
        """
        signature = kwargs.get("signature") 
        timestamp = kwargs.get("timestamp") 
        nonce = kwargs.get("nonce")
        response_msg = self._check_sign(signature, timestamp, nonce)
        if response_msg and request.httprequest.method == 'GET':
            echostr = kwargs.get("echostr")
            return echostr
        if not response_msg: #校验通不过，不是来自微信的消息
            return ""
        return ""
        openid = kwargs.get("openid")
        chat_xml = request.httprequest.data
        msg = parse_message(chat_xml)
        reply = TextReply(content='Received.', message=msg)
        xml = reply.render()
        return xml

    def _check_sign(self, signature, timestamp, nonce):
        token = request.env['ir.config_parameter'].sudo().get_param('wechat.token')
        try:
            check_signature(token, signature, timestamp, nonce)
            return True
        except InvalidSignatureException as e:
            #print(e)
            return False

    def _wx_openid(self, code):
        appid = request.env['ir.config_parameter'].sudo().get_param('wechat.appid')
        secret = request.env['ir.config_parameter'].sudo().get_param('wechat.appsecret')        
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid, secret, code)
        
        f = urllib.request.urlopen(url)
        response = f.read().decode('utf-8')
        dict_token = json.loads(response)
        if not dict_token.get("errcode", False):
            return dict_token
        else:
            raise SignupError("微信获取access_token/openid错误：err_code=%s, err_msg=%s" % (dict_token["errcode"], dict_token["errmsg"] ) )

    @http.route(['/wechat/signin', '/wechat/signin/<int:site_id>'], type='http', auth='none')
    def wx_signin(self, site_id=0, **kw):
        redirect = kw.pop('state', False)
        dbname = kw.pop('db', None)
        # 获取微信openid
        code = kw.pop('code', False)
        dict_token = self._wx_openid(code)
        openid = dict_token['openid']
        access_token = dict_token['access_token']  
        if not dbname:
            dbname = db_monodb()
        if not dbname:
            return BadRequest()
        if not http.db_filter([dbname]):
            return BadRequest()
        
        registry = registry_get(dbname)
        context = {}
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = env['res.users'].sudo().wx_auth(openid)
                cr.commit()
                url = '/web'
                if redirect:
                    url = redirect
                resp = login_and_redirect(*credentials, redirect_url=url)
                # Since /web is hardcoded, verify user has right to land on it
                if werkzeug.urls.url_parse(resp.location).path == '/web' and not request.env.user.has_group('base.group_user'):
                    resp.location = '/'
                return resp
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info('微信授权登录失败，转注册页面！')
                url = "/web/signup?site_id=%s&wx_openid=%s&access_token=%s" % (site_id, openid, access_token)
                redirect = request.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("微信授权登录错误: %s" % str(e))
                url = "/web/login"
        return set_cookie_and_redirect(url)
