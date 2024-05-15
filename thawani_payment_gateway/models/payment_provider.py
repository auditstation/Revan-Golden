# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


from odoo import fields, models, api, _


class DevConfig(models.TransientModel):
    _inherit = 'res.config.settings'


    delivery_done = fields.Boolean(default=True, string="Make delivery done after payment in thawani",
                               help="Make delivery done after payment in thawani")


    @api.model
    def get_values(self):
        res = super(DevConfig, self).get_values()
        res.update(
            delivery_done=self.env['ir.config_parameter'].sudo().get_param('thawani_payment_gateway.delivery_done')
        )
        return res


    def set_values(self):
        super(DevConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('thawani_payment_gateway.delivery_done', self.delivery_done)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('thawani', "Thawani")],
        ondelete={'thawani': 'set default'}
    )
    thawani_client_reference_id = fields.Char(string='Thawani Merchant ID', required_if_provider='thawani')
    thawani_secret_key = fields.Char(string='Thawani Secret Key', required_if_provider='thawani')
    thawani_publishable_key = fields.Char(string='Thawani publishable Key', required_if_provider='thawani')

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['thawani'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    def _thawani_get_api_url(self):
        """ Return the API URL according to the provider state.
        Note: self.ensure_one()
        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        if self.state == 'enabled':
            return 'https://checkout.thawani.om/'
        else:
            return 'https://uatcheckout.thawani.om/'
