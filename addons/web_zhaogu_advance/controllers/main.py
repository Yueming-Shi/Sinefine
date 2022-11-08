# -*- coding: utf-8 -*-
import datetime
import requests
import logging
import json
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
odoo_session = requests.Session()


class ZhaoguWeb(http.Controller):

    @http.route(['/order/trans/pendingclaim'], type='http', auth="user", website=True)
    def website_pendingclaim(self):

        shipping_order = request.env['shipping.bill'].sudo().search(
            [('state', '=', 'draft'), ('sale_order_id', '=', False)])

        value = {
            'shipping_orders': shipping_order
        }
        return request.render("web_zhaogu_advance.web_zhaogu_be_claimed_tree", value)

    @http.route(['/order/trans/unpaid'], type='http', auth="user", website=True)
    def website_unpaid(self):
        user = request.env.user
        partner = user.partner_id

        site_user = request.env['crm.team'].search([('user_id', '=', user.id)])

        if site_user and user.id != 2:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('state', '=', 'valued'), ('sale_site_id', '=', partner.id),
                 ('sale_invoice_payment_state', '=', '支付未完成')])
        else:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('sale_partner_id', '=', partner.id), ('state', '=', 'valued'),
                 ('sale_invoice_payment_state', '=', '支付未完成')])

        value = {
            'shipping_orders': shipping_order
        }
        return request.render("web_zhaogu_advance.web_zhaogu_be_paid_tree", value)

    @http.route(['/order/trans/tosign'], type='http', auth="user", website=True)
    def website_tosign(self):
        user = request.env.user
        partner = user.partner_id

        site_user = request.env['crm.team'].search([('user_id', '=', user.id)])

        if site_user and user.id != 2:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('state', '=', 'arrived'), ('sale_site_id', '=', partner.id)])
        else:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('sale_partner_id', '=', partner.id), ('state', '=', 'arrived')])

        value = {
            'shipping_orders': shipping_order
        }
        return request.render("web_zhaogu_advance.web_zhaogu_shipped_tree", value)

    @http.route(['/order/trans/signed'], type='http', auth="user", website=True)
    def website_signed(self):
        user = request.env.user
        partner = user.partner_id
        site_user = request.env['crm.team'].search([('user_id', '=', user.id)])

        if site_user and user.id != 2:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('state', '=', 'signed'), ('sale_site_id', '=', partner.id)])
        else:
            shipping_order = request.env['shipping.bill'].sudo().search(
                [('sale_partner_id', '=', partner.id), ('state', '=', 'signed')])

        value = {
            'shipping_orders': shipping_order
        }
        return request.render("web_zhaogu_advance.web_zhaogu_signed_tree", value)

    @http.route(['/order/shipping/detail/<int:page>'], type='http', auth="user", website=True)
    def website_shipping_order_detail(self, page):
        user = request.env.user
        sale_order = request.env['sale.order'].sudo().search([('id', '=', int(page))])
        if sale_order.partner_id.id == user.partner_id.id or sale_order.partner_team_site_id.id == user.partner_id.id:
            value = {
                'sale_order': sale_order,
            }
            return request.render("web_zhaogu_advance.web_zhaogu_shipping_detail_form", value)
        else:
            return request.redirect(request.httprequest.referrer)

    @http.route(['/payment/shipping'], type='http', auth="user", methods=['GET'], website=True)
    def website_shipping_payment(self, order=None, ):
        partner = request.env.user.partner_id
        shipping_order = request.env['shipping.bill'].browse(int(order))

        if shipping_order and shipping_order.sale_partner_id.id == partner.id:
            invoices_id = shipping_order.sale_order_id.invoice_ids[0]
            url = invoices_id.get_portal_url()
#            return request.redirect('/my/invoices/' + str(invoices_id) + '?access_token=' + str(request.csrf_token()))
            return request.redirect(url)
        else:
            return request.redirect(request.httprequest.referrer)

    @http.route(['/rebubble/shipping'], type='http', auth="user", methods=['GET'], website=True)
    def website_shipping_rebubble(self, order=None):
        partner = request.env.user.partner_id
        shipping_order = request.env['shipping.bill'].browse(int(order))

        if shipping_order and shipping_order.sale_partner_id.id == partner.id:
            shipping_order.has_changed = True
        return request.redirect(request.httprequest.referrer)

    @http.route(['/rebubbleno/shipping'], type='http', auth="user", methods=['GET'], website=True)
    def website_shipping_rebubbleno(self, order=None):
        partner = request.env.user.partner_id
        shipping_order = request.env['shipping.bill'].browse(int(order))

        if shipping_order and shipping_order.sale_partner_id.id == partner.id:
            shipping_order.has_changed = False
        return request.redirect('/order/trans/unpaid')

    @http.route(['/shpping/return/shipment'], type='http', auth="user", methods=['POST'], website=True)
    def website_shipping_return_shipment(self, **post):
        order_id = int(post.get('order_id'))
        order = request.env['shipping.bill'].sudo().browse(int(order_id))

        order.sudo().write({
            'has_returned': True,
            'return_address': post.get('address'),
            'return_contact': post.get('name'),
            'return_mobile': post.get('phone'),
            'return_name': order.name
        })

        return request.redirect(request.httprequest.referrer)

    @http.route(['/signin/shipping'], type='http', auth="user", methods=['GET'], website=True)
    def website_shipping_signin(self, order=None):
        partner = request.env.user.partner_id
        shipping_order = request.env['shipping.bill'].browse(int(order))

        if shipping_order and shipping_order.sale_partner_id.id == partner.id:
            shipping_order.state = 'signed'
            shipping_order.signed_date = datetime.now()
        return request.redirect('/order/trans/tosign')
