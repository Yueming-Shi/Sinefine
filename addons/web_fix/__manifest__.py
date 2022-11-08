# -*- coding: utf-8 -*-
{
    'name': "Fix No CSS $o-chatter-min-width",
    'description': """
        增加企业版模块documents需要的scss定义
    """,

    'author': "OSCG",
    'website': "http://www.oscg.cn",
    'category': 'base',
    'version': '15.0.1',
    'depends': ['web'],
    'data': [
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'web_fix/static/src/scss/secondary_variables.scss'),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
