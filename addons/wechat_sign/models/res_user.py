# -*- coding: utf-8 -*-



from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def create_wechat_user(self, res, team_id):
        '''
         {'openid': 'oTgF4uPJGuYDVEOXE0Te6gpOtYMI', 
         'nickname': '阿飞', 
         'sex': 0, 
         'language': '', 
         'city': '', 
         'province': '', 
         'country': '', 
         'headimgurl': 'https://thirdwx.qlogo.cn/mmopen/vi_32/AhaSicobIfA85ZUYjOZ26AfGAt1UsS0icY08UEibHxoT0mEg4kCuvibXBdruNP9kRkptXZ12ic2rWRyXNGwsZJWiaoag/132', 
         'privilege': []} 
        '''
        user = self.sudo().search([('wx_openid', '=', res['openid'])])
        if not user:
            val = {
                'name': res['nickname'],
                'login': res['openid'],
                'wx_openid': res['openid'],
                'groups_id': [(4, self.env.ref('base.group_portal').id)]
            }
            team_id = int(team_id)
            if not team_id:
                team_id = self.env['crm.team'].sudo().search([], limit=1).id
            val.update({'team_id': team_id})
            user = self.with_user(1).create(val)
        return user