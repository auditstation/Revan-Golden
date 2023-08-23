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
# Import required libraries (make sure it is installed!)
import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import requests
import json
from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'thawani':
            return res
        _logger.info("entered _get_specific_rendering_values")
        return self.execute_payment()
    
    
    # print(response.text)

    def execute_payment(self):
        """Fetching data and Executing Payment"""
        base_api_url = self.env['payment.provider'].search(
            [('code', '=', 'thawani')])._thawani_get_api_url()
        _logger.info('base_api_url')
        _logger.info(base_api_url)
        
        api_url = f"{base_api_url}api/v1/checkout/session"
        _logger.info('api_url')
        _logger.info(api_url)

        client_reference_id = self.env['payment.provider'].search([('code', '=',
                                                        'thawani')]).thawani_client_reference_id
        thawani_secret_key = self.env['payment.provider'].search([('code', '=',
                                                        'thawani')]).thawani_secret_key
        _logger.info('thawani_secret_key')
        _logger.info(thawani_secret_key)
        thawani_publishable_key = self.env['payment.provider'].search([('code', '=',
                                                        'thawani')]).thawani_publishable_key
        
        odoo_base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url')
        sale_order = self.env['payment.transaction'].search(
            [('id', '=', self.id)]).sale_order_ids

        order_line = self.env['payment.transaction'].search(
            [('id', '=', self.id)]).sale_order_ids.order_line
        invoice_items = [
            {
                'name': rec.product_id.name,
                'quantity': int(rec.product_uom_qty),
                'unit_amount': int(rec.price_unit) * 1000,
            }
            for rec in order_line
        ]
        # if len(self.partner_phone.replace('-', "").rsplit(' ', 1)[1]) > 11:
        #     raise ValidationError(
        #         _("Phone number must not  be greater than 11 characters"))
        
        ################################
        payload = json.dumps({
        "client_reference_id":str(client_reference_id) ,
        "mode": "payment",
        "products": invoice_items,
        "success_url": f"{odoo_base_url}/payment/thawani/success/{self.id}",
        # "success_url": "https://webhook.site/fa69f47b-5b18-4da2-91c8-8d0afff849d2",
        "cancel_url": f"{odoo_base_url}/payment/thawani/cancel/{self.id}",
        "metadata": {
            "Customer name": self.partner_name,
            "order id":sale_order.id ,
        }
        })
        _logger.info("payload")
        _logger.info(payload)
        headers = {
        'Content-Type': 'application/json',
        'thawani-api-key': str(thawani_secret_key)
        }

        response = requests.request("POST", api_url, headers=headers, data=payload)
        _logger.info(response)
        _logger.info('response')
        
        response_data = response.json()
        if not response_data.get('success') == True:
            raise ValidationError(f"{response_data.get('detail')}")
        if response_data.get('data')['session_id']:
            session_id = response_data.get('data')['session_id']
            self.provider_reference = session_id
            payment_url = f"{base_api_url}pay/{session_id}"
            _logger.info("payment_url")
            _logger.info(payment_url)

            # return request.redirect(payment_url)

            # return payment_url
        #     payload['PaymentURL'] = payment_url
        _logger.info("payment_url karim")
        _logger.info(payment_url)

        rendering_values ={
            'api_url': payment_url,
            'api_key': thawani_publishable_key
            #  'data': payload,
        }
        _logger.info("rendering_values karim")
        _logger.info(rendering_values)
        return rendering_values



    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Getting  payment status from myfatoorah"""
        _logger.info('_get_tx_from_notification_dataaaa')
        _logger.info(provider_code)
        _logger.info(notification_data)
        tx = super()._get_tx_from_notification_data(provider_code,
                                                        notification_data)
        tx_id = notification_data.get('id',False)
        tx = request.env['payment.transaction'].sudo().search([('id','=',int(tx_id))])
        if tx_id:
            # _logger.info(tx_id)
            _logger.info(tx)
            _logger.info(tx.provider_reference)
            
                # reference = response_data["Data"]["CustomerReference"]
                # domain.append(reference)
            # if tx := self.search(domain):
                        # return tx
            return tx
              
        # else:
        #     raise ValidationError(
        #         "thawani: " + _(
        #             "No transaction found matching reference %s.",
        #             reference)
        #     )

    def _handle_notification_data(self, provider_code, notification_data):
        tx = self._get_tx_from_notification_data(provider_code,
                                                 notification_data)
        _logger.info("_handle_notification_dataaa")
        _logger.info("provider_code",provider_code)
        _logger.info("notification_data",notification_data)
        tx._process_notification_data(notification_data)
        tx._execute_callback()
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'thawani':
            return
        tx_id = notification_data.get('id',False)
        tx = request.env['payment.transaction'].sudo().search([('id','=',int(tx_id))])
        _logger.info('_process_notification_data notification_dataaaa')
        _logger.info(notification_data)
        thawani_session = tx.provider_reference
        base_api_url = request.env['payment.provider'].search(
                    [('code', '=', 'thawani')])._thawani_get_api_url()
        _logger.info('base_api_url')
        _logger.info(base_api_url)
                
        api_url = f"{base_api_url}api/v1/checkout/session"
        _logger.info('api_url')
        _logger.info(api_url)

        client_reference_id = request.env['payment.provider'].search([('code', '=',
                                                                'thawani')]).thawani_client_reference_id
        thawani_secret_key = request.env['payment.provider'].search([('code', '=',
                                                                'thawani')]).thawani_secret_key
        _logger.info('thawani_secret_key')
        _logger.info(thawani_secret_key)
        thawani_publishable_key = request.env['payment.provider'].search([('code', '=',
                                                                'thawani')]).thawani_publishable_key
                
        odoo_base_url = request.env['ir.config_parameter'].get_param(
                    'web.base.url')
                
        url = f"{base_api_url}api/v1/checkout/session/{thawani_session}"
        _logger.info(url)

        headers = {
                    "Accept": "application/json",
                    "thawani-api-key": thawani_secret_key
                }

        response = requests.get(url, headers=headers)
        response_data = response.json()
        _logger.info("response_data")
        _logger.info(response_data)
       
            # if provider_code != 'thawani' or len(tx) == 1:
            #     return tx
        domain = [('provider_code', '=', 'thawani')]
        tx = request.env['payment.transaction'].sudo().search([('id','=',int(tx_id))])

        if response_data.get('success',False) == True and response_data.get('code',False) == 2000:
                    payment_status = response_data['data']['payment_status']
                    _logger.info('statusssss')
                    _logger.info(payment_status)
                    if payment_status == 'paid':
                        self._set_done()
                        _logger.info('paiiiiidd')
                    else:

                        message = "you cancelled your transaction"
                        self._set_canceled(message)
                        _logger.info('cancellleeed transaction')
                         
             
        