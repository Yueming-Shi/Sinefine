# -*- coding: utf-8 -*-
{
    'name':"OSCG-昆明兆古网站",
    'description':"""
        昆明兆古网站
    """,
    'category': 'Hidden',
    'version':'1.0',
    'depends':['base', 'web', 'website'],
    'data':[
        "views/web_zhaogu_be_paid_view.xml",
        "views/web_zhaogu_change_return_order_view.xml",
        "views/web_zhaogu_shipped_view.xml",
        "views/web_zhaogu_signed_view.xml",
        "views/web_zhaogu_shipping_detail_view.xml",
        "views/web_zhaogu_be_claimed_view.xml",
    ],
    'qweb':[

    ],
    'assets': {
            'web.assets_backend': [
                'web_zhaogu_advance/static/src/css/portal_orders.css',
            ],
        },
    'auto_install': False,
    'license': 'OEEL-1',
}
