# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.urls import url_join, url_encode

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    @http.route('/order/nocustomer', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_fill_order_create_view(self, waybill_no=False):
        values = {
            'user_name': request.env.user.name,
            'waybill_no': waybill_no
        }
        return request.render('zhaogu_sale.sale_portal_fill_order_create_template', values)

    @http.route('/sale/create/documents', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def sale_fill_order_create(self, **kwargs):
        user = request.env.user
        sale_shipping_no = request.env['sale.order'].sudo().search(
            [('shipping_no', '=', kwargs.get('shipping_no'))])

        if sale_shipping_no:
            values = {
                'user_name': request.env.user.name,
                'error_message': '运单号已存在。'
            }
            return request.render('zhaogu_sale.sale_portal_fill_order_create_template', values)
        else:
            values = {
                'partner_id': user.partner_id.id,
                'shipping_no': kwargs.get('shipping_no'),
            }
            sale_order = request.env['sale.order'].sudo().create(values)
            return request.redirect('/sale/portal/fill_order?order_id=' + str(sale_order.id))

    @http.route('/user/detail/edit', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def user_detail_edit(self):
        user = request.env.user
        partner = user.partner_id
        if not partner.street or not partner.city or not partner.state_id or not partner.zip or not partner.phone or not partner.country_id:
            return '400'
        else:
            return '200'

    @http.route('/sale/portal/fill_order', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_portal_fill_order(self, order_id=None, user_name=None, state=None, shipping_no=None, error_message=None,**kwargs):
       if request.env.user == request.env.ref('base.public_user'):
           redirect_url = '/sale/portal/fill_order?%s'%url_encode({'order_id':order_id,'shipping_no':shipping_no})
           return request.redirect('/web/login?redirect=%s'%redirect_url)
       sale_order = request.env['sale.order'].sudo().model_get_portal_order(force_id=order_id)
       values = {
           'order_id': sale_order.id,
           'state': state,
           'user_name': user_name or request.env.user.name,
           'shipping_no': sale_order.shipping_no or shipping_no or '',
           'lines': [{
               'product_sale_category_name':line.product_sale_category_id.name or '',
               'product_material_name':line.product_material_id.name or '',
               'product_brand_name':line.product_brand_id.name or '',
               'product_qty': line.product_uom_qty,
               'edit_url': '/sale/portal/fill_order_line?%s'%url_encode({'order_id':sale_order.id,'order_line_id':line.id}),
               'delete_url': '/sale/portal/delete_order_line?%s'%url_encode({'order_id':sale_order.id,'order_line_id':line.id}),
           } for line in sale_order.order_line],
           'error_message': error_message,
       }
       return request.render('zhaogu_sale.sale_portal_fill_order_template', values)


    @http.route('/sale/portal/fill_order_line', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def sale_portal_fill_order_line(self, order_id=None, order_line_id=None, shipping_no=None, **kwargs):
        sale_order = request.env['sale.order'].browse(int(order_id))
        if order_line_id:
            sale_order_line = sale_order.order_line.filtered(lambda l:l.id == int(order_line_id))
            product = sale_order_line.product_id
            sale_category_id, product_brand_id, product_material_id = product.sale_category_id.id,\
                                                        sale_order_line.brand_id.id, product.material_id.id
            qty = str(sale_order_line.product_uom_qty)
        else:
            sale_category_id, product_brand_id, product_material_id = kwargs.get('sale_category_id',''),\
                                    kwargs.get('product_brand_id', ''), kwargs.get('product_material_id','')
            qty = ''

        return request.render('zhaogu_sale.sale_portal_fill_order_line_template', {
            'order_id': sale_order.id,
            'order_line_id': order_line_id,
            'sale_categories': [(category.id, category.name) for category in request.env['product.sale.category'].search([])],
            'product_brands': [(material.id, material.name) for material in request.env['product.brand'].search([])],
            'product_materials':[(brand.id, brand.name) for brand in request.env['product.material'].search([])],
            'error_message': kwargs.get('error_message',''),
            'sale_category_id': sale_category_id,
            'product_brand_id': product_brand_id,
            'product_material_id': product_material_id,
            'qty': qty,
            'shipping_no': shipping_no,
        })

    @http.route('/sale/portal/delete', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_delete_order(self, order_id, **kwargs):
        sale_order = request.env['sale.order'].browse(int(order_id))
        sale_order.unlink()
        return request.redirect('/order/nocustomer')


    @http.route('/sale/portal/save', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_save_order(self, order_id=None, user_name=None, shipping_no=None, lines=None, **kwargs):
        try:
            sale_order = request.env['sale.order'].sudo().model_get_portal_order(force_id=order_id)
            if not shipping_no:
                return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                    {'order_id': order_id, 'shipping_no': shipping_no, 'error_message': '运单号不能为空'}))
            if not sale_order.order_line:
                return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                    {'order_id': order_id, 'shipping_no': shipping_no, 'error_message': '明细不能为空'}))

            sale_order.write({'shipping_no':shipping_no})
        except Exception as e:
            return request.redirect('/sale/portal/fill_order?%s' % url_encode(
                {'order_id': order_id, 'error_message': str(e)}))
        else:
            return request.redirect('/')

    @http.route('/sale/portal/save_line', type='http', auth='public', methods=['GET'], csrf=False)
    def sale_portal_save_order_line(self, order_id, order_line_id, sale_category_id, product_brand_id, product_material_id,
                                    qty, shipping_no=None,**kwargs):
        sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        try:
            sale_order.portal_update_line(sale_category_id, product_brand_id, product_material_id, qty, order_line_id)
        except UserError as e:
            params = {
                'order_id':order_id, 'error_message':str(e), 'order_line_id':order_line_id,
                'sale_category_id':sale_category_id, 'product_brand_id':product_brand_id,
                'product_material_id': product_material_id, 'qty':qty, 'shipping_no':shipping_no,
            }
            return request.redirect(f'/sale/portal/fill_order_line?%s'%url_encode(params))
        return request.redirect(f'/sale/portal/fill_order?%s'%url_encode({
            'order_id':order_id, 'shipping_no': sale_order.shipping_no or shipping_no}))


    @http.route('/sale/portal/orders', type='http', auth='public',website=True)
    def sale_portal_orders(self, ytype, **kwargs):
        partner = request.env.user.partner_id.id
        if request.env.user == request.env.ref('base.public_user'):
            redirect_url = '/sale/portal/orders'
            return request.redirect('/web/login?redirect=%s'%redirect_url)

        if ytype == 'all':
            sale_orders = request.env['sale.order'].sudo().search([('partner_id', '=', partner)])
        elif ytype == 'draft':
            sale_orders = request.env['shipping.bill'].sudo().search([('state', 'in', ['draft', 'paired']), ('sale_partner_id', '=', partner)]).mapped('sale_order_id')
        elif ytype == 'valuedno':
            sale_orders = request.env['shipping.bill'].sudo().search([('state', '=', 'valued'), ('sale_invoice_payment_state', '=', '支付未完成'), ('sale_partner_id', '=', partner)]).mapped('sale_order_id')
        elif ytype == 'valued':
            sale_orders = request.env['shipping.bill'].sudo().search(
                [('state', '=', 'valued'), ('sale_invoice_payment_state', '=', '支付已完成'), ('sale_partner_id', '=', partner)]).mapped('sale_order_id')
        elif ytype == 'arrived':
            sale_orders = request.env['shipping.bill'].sudo().search([('state', '=', 'arrived'), ('sale_partner_id', '=', partner)]).mapped('sale_order_id')
        else:
            return request.redirect(request.httprequest.referrer)

        values = {'sale_orders':sale_orders}
        return request.render('zhaogu_sale.sale_portal_orders_template', values)


