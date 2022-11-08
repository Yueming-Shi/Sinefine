# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char('名称')
    is_in_blacklist = fields.Boolean('是黑名单')


