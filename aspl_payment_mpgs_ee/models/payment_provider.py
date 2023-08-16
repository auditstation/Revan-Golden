# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models


class ProviderMasterCard(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('mpgs', 'MPGS')], ondelete={'mpgs': 'set default'})
    merchant_id = fields.Char(string='Merchant Id', required_if_provider='mpgs', groups='base.group_user')
    merchant_name = fields.Char(string='Merchant Name', required_if_provider='mpgs', groups='base.group_user')
    mpgs_secret_key = fields.Char(string='MPGS Secret Key', required_if_provider='mpgs', groups='base.group_user')
    address1 = fields.Char(string="Address1", required_if_provider='mpgs', groups='base.group_user')
    address2 = fields.Char(string="Address2", required_if_provider='mpgs', groups='base.group_user')
