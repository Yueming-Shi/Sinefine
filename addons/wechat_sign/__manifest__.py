{
    'name': "微信公众号登录",
    'version': '15.0.1',
    'category': 'Marketing/Social Marketing',
    'author': 'OSCG',
    'website': 'http://www.oscg.cn',
    'sequence': 350,
    'depends': ['sale', 'wechat_bizmsg'],
    'demo': [],
    'data': [
        'views/sale_view.xml',
        'views/template.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wechat_sign/static/src/css/login.css',
        ],
    },
    'installable': True,
    'application': False,
}
