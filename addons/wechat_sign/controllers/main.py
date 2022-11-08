# -*- coding: utf-8 -*-
import logging
import qrcode
import base64
from io import BytesIO
from wechatpy.oauth import WeChatOAuth

from odoo import  http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import SIGN_UP_REQUEST_PARAMS
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


SIGN_UP_REQUEST_PARAMS.update({'site_id'})
_logger = logging.getLogger(__name__)



def make_qrcode(self, qrurl):
    """generate qrcode from url"""
    img = qrcode.make(qrurl)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    heximage = base64.b64encode(buffer.getvalue())
    return "data:image/png;base64,{}".format(heximage.decode('utf-8'))
http.HttpRequest.make_qrcode = make_qrcode
class PortalAccount(CustomerPortal):

    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'teams_count' in counters:
            teams_count = request.env['crm.team'].sudo().search_count([])
            values['teams_count'] = teams_count
        return values

    @http.route(['/my/teams', '/my/teams/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_teams1(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        TeamsEnv = request.env['crm.team'].sudo()
        domain = []
        teams_count = TeamsEnv.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/teams",
            total=teams_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        teams = TeamsEnv.search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'teams': teams,
            'page_name': 'Teams',
            'pager': pager,
            'default_url': '/my/teams',
        })
        return request.render("wechat_sign.portal_my_teams", values)


class AuthSignupHome(AuthSignupHome):

    def list_teams(self):
        return request.env['crm.team'].sudo().search([])
        
    def get_auth_signup_qcontext(self):
        result = super(AuthSignupHome, self).get_auth_signup_qcontext()
        result["teams"] = self.list_teams()
        base_url = request.httprequest.base_url
        _logger.info(base_url)
        result['baes_url'] = base_url
        return result

    def _wechat_instance(self, site_id=0):
        appid = request.env['ir.config_parameter'].sudo().get_param('wechat.appid')
        secret = request.env['ir.config_parameter'].sudo().get_param('wechat.appsecret')        
        base_url = request.httprequest.url_root
        url = '%swechat/signin/%s' % (base_url, site_id)
       
        wechat_auth = WeChatOAuth(appid, secret, url, 'snsapi_userinfo')  
        return wechat_auth

    @http.route(['/wechat/login', '/wechat/login/<int:site>'], type='http', auth='public', website=True, sitemap=False)
    def wechat_login(self, site=0, *args, **kw):
        wechat_auth = self._wechat_instance(site)  
        authorize_url = wechat_auth.authorize_url
        _logger.info(authorize_url)   
        return  request.redirect(authorize_url, 301, False) 

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        _logger.info(kw)   
        if kw.get('wx_openid', False) and kw.get('access_token', False):
            #如果没有用户 则再获取用户信息 创建用户
            site = kw.get('site_id', 0)
            wechat_auth = self._wechat_instance(site)  
            res = wechat_auth.get_user_info(kw['wx_openid'], kw['access_token'])
            res = request.env['res.users'].create_wechat_user(res, site)
            if res:
                wechat_auth = self._wechat_instance(site)  
                authorize_url = wechat_auth.authorize_url
                _logger.info(authorize_url)   
                return  request.redirect(authorize_url, 301, False) 
            else:
                return request.redirect('/404')

        user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
        if user_agent.find('MicroMessenger') > -1:
            wechat_auth = self._wechat_instance(kw.get('site_id', 0))  
            authorize_url = wechat_auth.authorize_url
            _logger.info(authorize_url)   
            return  request.redirect(authorize_url, 301, False) 
        return super().web_auth_signup(*args, **kw)

    def _prepare_signup_values(self, qcontext):
        value = super()._prepare_signup_values(qcontext)
        if qcontext.get('site_id'):
            value.update({
                'team_id': qcontext.get('site_id')
            })
        #base_url = request.httprequest.base_url
        #_logger.info(base_url)
        #value['baes_url'] = base_url
        return value

    @http.route('/web/site/list', type='http', auth='public', website=True, sitemap=False)
    def site_list(self):
        sites = request.env['crm.team'].sudo().search([])
        return request.render("wechat_sign.sitelist", {'sites': sites})
 