import logging
import pprint
import json
import requests
from odoo import http
from odoo.http import request
import ast

_logger = logging.getLogger(__name__)

class PaymentMyFatoorahController(http.Controller):
    _success_url = '/payment/thawani/success'
    # _failure_url = '/payment/thawani/failure'
    _cancel_url = '/payment/thawani/cancel'
    # _notification_url = '/payment/thawani/notification'

    @http.route([_success_url,
                    _cancel_url,
                    ], type='http', methods=['GET'], auth='public')
    def thawani_return_from_checkout(self, **data):
        """ Process the notification data sent by Tamara Pago after redirection from checkout.

        :param dict data: The notification data.
        """
        # Handle the notification data.
        _logger.info("Handling redirection from Thawani with data:\n%s", pprint.pformat(data))
        _logger.info("request from Thawani with data:\n%s", pprint.pformat(vars(request)))
        # {'decline_type': 'soft decline',
        # 'orderId': '475ae32f-c049-496a-950d-a5691730cd57',
        # 'paymentStatus': 'declined'
        # paymentStatus}
        if data.get('orderId') != 'null':
            request.env['payment.transaction'].sudo()._handle_notification_data(
                'tamara', data
            )
        else:  # The customer cancelled the payment by clicking on the return button.
            pass  # Don't try to process this case because the payment id was not provided.

        # Redirect the user to the status page.
        return request.redirect('/payment/status')

