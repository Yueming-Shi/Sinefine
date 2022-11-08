# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_category_id = fields.Many2one('product.sale.category','销售分类')
    material_id = fields.Many2one('product.material','材质')

    @api.model
    def model_find_from_portal(cls, sale_category_id, material_id):
        self = cls.search([('sale_category_id','=',sale_category_id),('material_id','=',material_id),],limit=1)
        if not self:
            sale_category = cls.env['product.sale.category'].browse(sale_category_id)
            material = cls.env['product.material'].browse(material_id)
            self = cls.create({
                'name': f'{sale_category.name}-{material.name} 待更正sku',
                'sale_category_id': sale_category_id,
                'material_id': material_id,
                'type': 'product',
            })
        return self

    @api.constrains('sale_category_id','material_id',)
    def check_sale_category__material_unique(selfs):
        for self in selfs:
            if self.sale_category_id and self.material_id:
                if selfs.search_count([('sale_category_id','=',self.sale_category_id.id),
                    ('material_id','=',self.material_id.id),('id','!=',self.id)]):
                    raise UserError(f'产品中 {self.sale_category_id.name} + {self.material_id.name}'\
                        f' 已存在')

