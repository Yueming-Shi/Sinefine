# -*- coding: utf-8 -*-

import io
import qrcode
import base64

from odoo import api, fields, models
from odoo.tools.misc import ustr
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_oauth.controllers.main import OAuthLogin

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    qrcode = fields.Image(
        attachment=False, store=True, readonly=False)

    def generate_qrcode(self):
        url = '%s/web/signup?site_id=%s' %(self.env['ir.config_parameter'].get_param('web.base.url'), self.id)
        data = io.BytesIO()
        qrcode.make(url.encode(), box_size=4).save(data, optimise=True, format='PNG')
        self.write({
            'qrcode':  base64.b64encode(data.getvalue()).decode()
        })