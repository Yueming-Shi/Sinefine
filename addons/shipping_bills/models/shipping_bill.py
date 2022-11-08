# import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging, math
_logger = logging.getLogger(__name__)


class ShippingBill(models.Model):
    _name = 'shipping.bill'
    _inherit = 'mail.thread'
    _description = 'Shipping Bill'

    state = fields.Selection([('draft','草稿'),('paired','已匹配'),('valued','已计费'),
                              ('returned','已退运'),('transported','已转运'),('arrived','已到站点'),
                              ('signed','已签收'),('discarded','丢弃')],default='draft',string='状态')

    ref = fields.Char(string='参考号（每天）',copy=False)

    # 草稿
    in_date = fields.Date(string='入库日期',tracking=True,)
    name = fields.Char('运单号',copy=False,tracking=True,)
    picking_code = fields.Char('仓库取件码',copy=False,tracking=True,)
    length = fields.Float(string='长度(cm)',tracking=True,)
    width = fields.Float(string='宽度(cm)',tracking=True,)
    height = fields.Float(string='高度(cm)',tracking=True,)
    actual_weight = fields.Float('实际重量(KG)', digits=(10, 1),tracking=True,)
    uom_id = fields.Many2one('uom.uom','单位')
    shipping_factor_id = fields.Many2one('shipping.factor', '线路敏感性', required=True,tracking=True,)

    # 已匹配
    sale_order_id = fields.Many2one('sale.order','销售单')
    sale_fetch_no = fields.Char('订单取件码',related='sale_order_id.fetch_no',store=True)
    sale_partner_id = fields.Many2one('res.partner','销售客户',related='sale_order_id.partner_id',store=True)
    sale_site_id = fields.Many2one(string='站点',related='sale_order_id.partner_team_site_id',store=True)
    sale_site_contact_address = fields.Char('站点地址',related='sale_order_id.partner_team_site_contact_address',store=True)

    # 已计费
    size_weight = fields.Float('计费重量',tracking=True,)
    fee = fields.Float(string='费用',tracking=True,)
    currency_id = fields.Many2one('res.currency','币种',tracking=True,)

    # 已付款
    sale_invoice_ids = fields.Many2many('account.move',string='结算单号',related='sale_order_id.invoice_ids')

    def _compute_sale_invoice_payment_state(selfs):
        for self in selfs:
            invoices = self.sale_invoice_ids
            if invoices and invoices[-1].payment_state == 'paid':
                sale_invoice_payment_state = '支付已完成'
            else:
                sale_invoice_payment_state = '支付未完成'
            self.sale_invoice_payment_state = sale_invoice_payment_state

    def _search_sale_invoice_payment_state(cls, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        if operator == '=':
            selfs = cls.search([]).filtered(lambda s:s.sale_invoice_payment_state == value)
        else:
            selfs = cls.search([]).filtered(lambda s:s.sale_invoice_payment_state != value)
        return [('id','in',selfs.ids)]
    sale_invoice_payment_state = fields.Char('付款状态',compute='_compute_sale_invoice_payment_state',search='_search_sale_invoice_payment_state')

    # 已转运
    out_date = fields.Date(string='出库时间')
    logistics = fields.Char(string='物流商')
    tracking_no = fields.Char('物流追踪码')

    # 已退运
    has_bought_safety = fields.Boolean('购买保险')
    can_change = fields.Boolean('可改泡')
    has_changed = fields.Boolean('申请改泡')
    has_returned = fields.Boolean('退运')
    return_address = fields.Char('退运地址')
    return_contact = fields.Char('退运收件人')
    return_mobile = fields.Char('退运联系电话')
    return_name = fields.Char('退运单号')
    returned_date = fields.Date('退运日期')
    in_days = fields.Integer('入库天数')

    # 已到站
    arrived_date = fields.Date('站点签收日期')

    # 已签收
    signed_date = fields.Date('客户签收日期')

    # 丢弃
    discarded_date = fields.Date('丢弃日期')

    @api.model
    def create(cls, values):
        if not values.get('ref'):
            values['ref'] = cls.env['ir.sequence'].next_by_code('shipping.bill')
        return super().create(values)

    # 匹配预报单
    def multi_action_match(selfs):
        for self in selfs.filtered(lambda s:s.name and not s.sale_order_id):
            sale_order = selfs.env['sale.order'].search([('shipping_no','=',self.name),('shipping_bill_id','=',False)],limit=1)
            if not sale_order:
                continue
            sale_order.write({'shipping_bill_id': self.id, 'fetch_no':self.picking_code})
#            sale_order.set_fetch_no()
            self.write({'sale_order_id':sale_order.id, 'state':'paired'})

    def multi_action_compute(selfs):
        for self in selfs:
            if not self.length or not self.width or not self.height or not self.shipping_factor_id or not self.actual_weight:
                continue
            volume = self.length * self.width * self.height  # 体积
            shipping_factor = self.shipping_factor_id

            size_weight = max([self.actual_weight, volume/shipping_factor.factor])
            weight = math.ceil(size_weight * 1000 / shipping_factor.next_weight_to_ceil) * shipping_factor.next_weight_to_ceil

            if weight < shipping_factor.first_weight:
                fee = shipping_factor.first_total_price
            else:
                fee = shipping_factor.first_total_price + (weight - shipping_factor.first_weight) / shipping_factor.next_weight_to_ceil * shipping_factor.next_price_unit

            self.write({'fee': fee, 'currency_id': shipping_factor.currency_id.id, 'state':'valued',
                        'size_weight':size_weight, })

        if not selfs._context.get('force_stop'):
            selfs.action_remind_payment()

    def action_remind_payment(selfs):
        for self in selfs:
            fee, so = self.fee, self.sale_order_id
            if not (fee and so):
                continue

            shipping_factor = self.shipping_factor_id  # 线路
            volume_factor = shipping_factor.factor  # 体积重系数

            volume = self.length * self.width * self.height
            weight = int(volume / volume_factor) # 体积/

            actual_weight = math.ceil(self.actual_weight * 1000 )  # 实际重量
            if weight < actual_weight:
                weight = actual_weight  # 最终计算重量

            description = "包裹体积(立方厘米)：{}\n包裹重量（kg）：{}\n线路敏感性：{}\n体积重系数{}".format(
                volume, weight / 10, shipping_factor.name, volume_factor)

            product_name = f'运费({self.shipping_factor_id.name})'
            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            if not product:
                raise UserError('没有找到运费')
            self.env['sale.order.line'].create({
                "product_id": product.id,
                "name": description,
                "product_uom_qty": 1.0,
                "product_uom": product.uom_id.id,
                "price_unit": fee,
                'order_id': so.id
            })
            so.action_confirm()
            invoice = so._create_invoices(True)
            invoice.action_post()

    @api.constrains('name')
    def check_name_unique(selfs):
        for self in selfs:
            if self.name:
                if selfs.search_count([('name','=',self.name),('id','!=',self.id)]):
                    raise UserError(f'运单号= {self.name} 已存在')
                    
    @api.constrains('picking_code')
    def check_picking_code_unique(selfs):
        for self in selfs:
            if self.picking_code:
                if selfs.search_count([('picking_code','=',self.picking_code),('id','!=',self.id)]):
                    raise UserError(f'取件码= {self.picking_code} 已存在')

    @api.constrains('ref')
    def check_ref_unique(selfs):
        for self in selfs:
            if self.ref:
                if selfs.search_count([('ref','=',self.ref),('id','!=',self.id)]):
                    raise UserError(f'参考号= {self.ref} 已存在')
    @api.model
    def model_update_in_days(cls):
        for self in cls.search([('returned_date','!=',False)]):
            self.in_days += 1