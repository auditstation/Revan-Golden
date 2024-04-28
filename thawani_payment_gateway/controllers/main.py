import logging
import pprint
import json
import requests
from odoo import http
from odoo.http import request
import ast
import logging
from datetime import timedelta

import psycopg2

from odoo import fields


_logger = logging.getLogger(__name__)



class PaymentMyFatoorahController(http.Controller):
    _success_url = '/payment/thawani/success/<int:tx_id>'
    # _failure_url = '/payment/thawani/failure'
    _cancel_url = '/payment/thawani/cancel/<int:tx_id>'
    # _notification_url = '/payment/thawani/notification'

    @http.route([_success_url,
                    _cancel_url,
                    ], type='http', methods=['GET'], auth='public',website=True)
    def thawani_return_from_checkout(self, **data):
        """ Process the notification data sent by Tamara Pago after redirection from checkout.

        :param dict data: The notification data.
        """
        # Handle the notification data.
        _logger.info("Handling redirection from Thawani with data:\n%s", pprint.pformat(data))
        _logger.info("returned from checout:\n%s", pprint.pformat(self._success_url))
        _logger.info("request from Thawani with data:\n%s", pprint.pformat(vars(request.httprequest)))
        # {'decline_type': 'soft decline',
        # 'orderId': '475ae32f-c049-496a-950d-a5691730cd57',
        # 'paymentStatus': 'declined'
        # paymentStatus}
        tx_id= False
        tx_id = data.get('tx_id',False)
        _logger.info("tx_idddd")
        _logger.info(tx_id)
        if tx_id:
             handle = request.env['payment.transaction'].sudo()._handle_notification_data(
                        'thawani', {'id':int(tx_id),}
                    )
        # else:
        #     handle = request.env['payment.transaction'].sudo()._handle_notification_data(
        #                 'thawani', {'cancelled':'cancelled',
        #                             'id':False}
        #             )

             
        #     tx = request.env['payment.transaction'].sudo().search([('id','=',int(tx_id))])
        #     _logger.info(tx_id)
        #     _logger.info(tx)
        #     _logger.info(tx.provider_reference)
        #     thawani_session = tx.provider_reference
        #     base_api_url = request.env['payment.provider'].search(
        #     [('code', '=', 'thawani')])._thawani_get_api_url()
        #     _logger.info('base_api_url')
        #     _logger.info(base_api_url)
            
        #     api_url = f"{base_api_url}api/v1/checkout/session"
        #     _logger.info('api_url')
        #     _logger.info(api_url)

        #     client_reference_id = request.env['payment.provider'].search([('code', '=',
        #                                                     'thawani')]).thawani_client_reference_id
        #     thawani_secret_key = request.env['payment.provider'].search([('code', '=',
        #                                                     'thawani')]).thawani_secret_key
        #     _logger.info('thawani_secret_key')
        #     _logger.info(thawani_secret_key)
        #     thawani_publishable_key = request.env['payment.provider'].search([('code', '=',
        #                                                     'thawani')]).thawani_publishable_key
            
        #     odoo_base_url = request.env['ir.config_parameter'].get_param(
        #         'web.base.url')
            
        #     url = f"{base_api_url}api/v1/checkout/session/{thawani_session}"
        #     _logger.info(url)

        #     headers = {
        #         "Accept": "application/json",
        #         "thawani-api-key": thawani_secret_key
        #     }

        #     response = requests.get(url, headers=headers)
        #     response_data = response.json()
        #     if response_data.get('success',False) == True and response_data.get('code',False) == 2000:
        #         payment_status = response_data.get('payment_status',False)
        #         if payment_status == 'paid':
        #             _logger.inf('paiiiiidd')
       
            




        # if data.get('orderId') != 'null':
        #     request.env['payment.transaction'].sudo()._handle_notification_data(
        #         'thawani', data
        #     )
        # else:  # The customer cancelled the payment by clicking on the return button.
        #     pass  # Don't try to process this case because the payment id was not provided.

        # Redirect the user to the status page.
        
        website_id = request.website.domain
        if website_id:
            return request.redirect(website_id +'/payment/status')
        # else:
        #     return request.redirect('/payment/status')  

