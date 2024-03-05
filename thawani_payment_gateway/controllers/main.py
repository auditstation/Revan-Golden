import logging
import pprint
import json
import requests
from odoo import http
from odoo.http import request
import ast
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
import logging
from datetime import timedelta

import psycopg2

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

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
        
        website_id = request.website.id
        
        test = request.env['res.config.settings'].sudo().search([('website_id','=',website_id)])
        _logger.info(f'ggggggggggggg{website_id,test.website_domain}')
        
        return request.redirect('https://www.classycom.net/payment/status')

class PaymentPostProcessingInherit(PaymentPostProcessing):
    @http.route('/payment/status/poll', type='json', auth='public')
    def poll_status(self, **_kwargs):
        """ Fetch the transactions to display on the status page and finalize their post-processing.

        :return: The post-processing values of the transactions
        :rtype: dict
        """
        # Retrieve recent user's transactions from the session
        limit_date = fields.Datetime.now() - timedelta(days=1)
        monitored_txs = request.env['payment.transaction'].sudo().search([
            ('id', 'in', self.get_monitored_transaction_ids()),
            ('last_state_change', '>=', limit_date)
        ])
        _logger.info(f'w3wwwwwwwwwwwwwww{monitored_txs}')
       
        if not monitored_txs:  # The transaction was not correctly created
            _logger.info(f'ddddddddddddd{monitored_txs}')
            return {
                'success': False,
                'error': 'no_tx_found',
            }

        # Build the list of display values with the display message and post-processing values
        display_values_list = []
        for tx in monitored_txs:
            display_message = None
            if tx.state == 'pending':
                display_message = tx.provider_id.pending_msg
            elif tx.state == 'done':
                display_message = tx.provider_id.done_msg
            elif tx.state == 'cancel':
                display_message = tx.provider_id.cancel_msg
            display_values_list.append({
                'display_message': display_message,
                **tx._get_post_processing_values(),
            })

        # Stop monitoring already post-processed transactions
        post_processed_txs = monitored_txs.filtered('is_post_processed')
        self.remove_transactions(post_processed_txs)

        # Finalize post-processing of transactions before displaying them to the user
        txs_to_post_process = (monitored_txs - post_processed_txs).filtered(
            lambda t: t.state == 'done'
        )
        success, error = True, None
        try:
            txs_to_post_process._finalize_post_processing()
        except psycopg2.OperationalError:  # A collision of accounting sequences occurred
            request.env.cr.rollback()  # Rollback and try later
            success = False
            error = 'tx_process_retry'
        except Exception as e:
            request.env.cr.rollback()
            success = False
            error = str(e)
            _logger.exception(
                "encountered an error while post-processing transactions with ids %s:\n%s",
                ', '.join([str(tx_id) for tx_id in txs_to_post_process.ids]), e
            )

        return {
            'success': success,
            'error': error,
            'display_values_list': display_values_list,
        }
