# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_sale_category_id = fields.Many2one(related='product_id.sale_category_id',store=True)
    product_material_id = fields.Many2one(related='product_id.material_id',store=True)
    product_brand_id = fields.Many2one(related='product_id.brand_id',store=True)



