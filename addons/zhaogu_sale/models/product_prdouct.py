# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_category_id = fields.Many2one('product.sale.category','销售分类')
    material_id = fields.Many2one('product.material','材质')
    brand_id = fields.Many2one('product.brand','品牌')

    @api.model
    def model_find_from_portal(cls, sale_category_id, brand_id, material_id):
        self = cls.search([('sale_category_id','=',sale_category_id),('material_id','=',material_id),
                           ('brand_id','=',brand_id)],limit=1)
        if not self:
            self = cls.create({
                'name': '待更正sku',
                'sale_category_id': sale_category_id,
                'material_id': material_id,
                'brand_id': brand_id,
            })
        return self

    @api.constrains('sale_category_id','material_id','brand_id')
    def check_sale_category__material__brand_unique(selfs):
        for self in selfs:
            if self.sale_category_id and self.material_id and self.brand_id:
                if selfs.search_count([('sale_category_id','=',self.sale_category_id.id),
                    ('material_id','=',self.material_id.id),
                    ('brand_id','=',self.brand_id.id),('id','!=',self.id)]):
                    raise UserError(f'产品中 {self.sale_category_id.name} + {self.material_id.name}'\
                        f'+ {self.brand_id.name} 已存在')

