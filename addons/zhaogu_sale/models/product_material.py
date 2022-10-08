# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductMaterial(models.Model):
    _name = 'product.material'

    name = fields.Char('名称')


