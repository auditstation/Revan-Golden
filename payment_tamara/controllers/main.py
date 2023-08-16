

import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo import http
from odoo.http import request

class Hospital(http.Controller):


    @http.route('/get_patients', type='json', auth='user')
    def get_patients(self):
        print("Yes here entered")
        patients_rec = request.env['res.partner'].search([])
        patients = []
        for rec in patients_rec:
            vals = {
                'id': rec.id,
                'name': rec.name,
            }
            patients.append(vals)
        print("Patient List--->", patients)
        data = {'status': 200, 'response': patients, 'message': 'Done All Patients Returned'}
        return patients

_logger = logging.getLogger(__name__)


class TamaraController(http.Controller):
    _success_url = '/payment/tamara/success'
    _failure_url = '/payment/tamara/failure'
    _cancel_url = '/payment/tamara/cancel'
    _notification_url = '/payment/tamara/notification'


    @http.route(_notification_url, type='json',auth='public')
    def tamara_notification(self):
        payload = request.dispatcher.jsonrequest
        api_token = request.httprequest.headers.get('Authorization').split(' ')[1]
        if payload:
            order_id = payload.get('orderId')
            order_reference_id = payload.get('orderReferenceId')
            order_status = payload.get('orderStatus')
            transaction_id = request.env['payment.transaction'].sudo().search([('tamara_order_id', '=', order_id)])
            provider = transaction_id.provider_id
            # if provider_id.tamara_notification_token != api_token:
            # else:
            
            
    @http.route([_success_url,
                 _failure_url,
                 _cancel_url,
                 ], type='http', methods=['GET'], auth='public')
    def tamara_return_from_checkout(self, **data):
        """ Process the notification data sent by Tamara Pago after redirection from checkout.

        :param dict data: The notification data.
        """
        # Handle the notification data.
        _logger.info("Handling redirection from Tamara with data:\n%s", pprint.pformat(data))
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

