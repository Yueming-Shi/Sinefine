# See LICENSE file for full copyright and licensing details.

{
    'name': 'zhaogu_sale',
    'depends': [
        'sale','shipping_bills','website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/action.xml',
        'views/menu.xml',
        'views/product_product.xml',
        'views/sale_order_line.xml',
        'views/product_brand.xml',
        'views/product_material.xml',
        'views/product_sale_category.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
