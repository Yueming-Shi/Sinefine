# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductSaleCategory(models.Model):
    _name = 'product.sale.category'

    name = fields.Char('名称')


