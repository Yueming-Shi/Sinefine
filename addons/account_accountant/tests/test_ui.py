# -*- coding: utf-8 -*-
# Part of Odoo.

import odoo.tests


@odoo.tests.tagged('-at_install', 'post_install')
class TestUi(odoo.tests.HttpCase):
    def test_accountant_tour(self):
        self.start_tour("/web", 'account_accountant_tour', login="admin")
