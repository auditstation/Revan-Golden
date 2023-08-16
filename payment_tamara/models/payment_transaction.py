

import logging
import pprint

from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_tamara.controllers.main import TamaraController
from odoo.addons.payment_tamara.const import TRANSACTION_STATUS_MAPPING
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    tamara_order_id = fields.Char("Tamara Order ID", readonly=True, copy=False, index=True)
    tamara_checkout_id = fields.Char("Tamara Checkout ID", readonly=True, copy=False)
    tamara_status = fields.Char("Tamara Status", readonly=True, copy=False)
    tamara_capture_id = fields.Char("Tamara Capture ID", readonly=True, copy=False)
    tamara_refund_id = fields.Char("Tamara Refund ID", readonly=True, copy=False)
    tamra_cancel_id = fields.Char("Tamara Cancel ID", readonly=True, copy=False)
    
    def action_cancel(self):
        """ Check the state of the transaction and request to have them voided. """
        if any(tx.state != 'done' for tx in self):
            raise ValidationError(_("Only done transactions can be cancelled."))
        if any(tx.provider_id.code != 'tamara' for tx in self):
            raise ValidationError(_("Only Tamara transactions can be cancelled."))
        payment_utils.check_rights_on_recordset(self)
        for tx in self:
            # In sudo mode because we need to be able to read on provider fields.
            tx.sudo()._send_void_request()
            
    def _send_void_request(self):
        """ Override of payment to send a void request to Tamara.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_void_request()
        if self.provider_code != 'tamara':
            return

        data = {
            'total_amount': {
                "amount": self.amount,
                "currency": self.currency_id.name
                
            }

        }
        response_content = self.provider_id._tamara_make_request(
            f'orders/{self.tamara_order_id}/cancel', payload=data
        )
        _logger.info("void request response:\n%s", pprint.pformat(response_content))

        # Handle the void request response
        status = response_content.get('status', False)
        cancel_id = response_content.get('cancel_id', False)
        if cancel_id:
            self.tamra_cancel_id = cancel_id
            self._set_canceled()
            
            
            
    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return Mercado Pago-specific rendering values.

        Note: self.ensure_one() from `_get_rendering_values`.

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'tamara':
            return res

        # Initiate the payment and retrieve the payment link data.
        payload = self._tamara_prepare_checkout_session_payload()
        _logger.info(
            "Sending '/checkout' request for link creation:\n%s",
            pprint.pformat(payload),
        )
        resp = self.provider_id._tamara_make_request(
            '/checkout', payload=payload
        )
        api_url = resp.get('checkout_url')
        self.tamara_checkout_id = resp.get('checkout_id')
        self.tamara_order_id = resp.get('order_id')
        self.provider_reference = resp.get('order_id')
        # Extract the payment link URL and embed it in the redirect form.
        rendering_values = {
            'api_url': api_url,
        }
        return rendering_values

    def _tamara_prepare_checkout_session_payload(self):
        """ Create the payload for the preference request based on the transaction values.

        :return: The request payload.
        :rtype: dict
        """
        orders = self.sale_order_ids
        invoices = self.invoice_ids
        ref = ""
        items = []
        partner_first_name = ""
        partner_last_name = ""
        tax_amount = {}
        base_url = self.provider_id.get_base_url()
        success_url = urls.url_join(base_url, TamaraController._success_url)
        failure_url = urls.url_join(base_url, TamaraController._failure_url)
        cancel_url = urls.url_join(base_url, TamaraController._cancel_url)
        notification_url = urls.url_join(base_url, TamaraController._notification_url)
          # Append the reference to identify the transaction from the webhook notification data.
        if self.partner_id:
            name = self.partner_name.split(" ")
            if len(name) > 1:
                partner_first_name = name[0][:49]
                partner_last_name = name[1][:49]
            elif len(name) == 1:
                partner_first_name = name[0][:49]
                partner_last_name = name[0][:49]
            else:
                partner_first_name = self.partner_id.name[:49]
                partner_first_name = self.partner_id.name[:49]
                
        if orders:
            order_id = orders[0]
            ref = order_id.name
            tax_amount = {
                            "amount": str(order_id.amount_tax),
                            "currency": order_id.currency_id.name
            }
            for line in order_id.order_line:
                items_dict = {
                                "reference_id": line.product_id.id,
                                "type": line.product_id.type,
                                "name": line.product_id.name[:254] ,
                                "sku": (line.product_id.default_code or '')[:127] or (line.product_id.name or '')[:127] or (line.name or '')[:127],
                                "quantity": int(line.product_uom_qty),
                                "total_amount": {
                                                "amount": str(line.price_total),
                                                "currency": line.currency_id.name
                                                }
                            }
                items.append(items_dict)
        if invoices:
            invoice_id = invoices[0]
            ref = invoice_id.name
            tax_amount = {
                            "amount": str(invoice_id.amount_tax),
                            "currency": invoice_id.currency_id.name
            }
            for line in invoice_id.invoice_line_ids:
                items_dict = {
                                "reference_id": line.product_id.id or line.name,
                                "type": line.product_id.type or "service",
                                "name": line.product_id.name[:254] or line.name[:254] ,
                                "sku": (line.product_id.default_code or '')[:127] or (line.product_id.name or '')[:127] or (line.name or '')[:127],
                                "quantity": int(line.quantity),
                                "total_amount": {
                                                "amount": str(line.price_total),
                                                "currency": line.currency_id.name
                                                }
                            }
                items.append(items_dict)
        return {
            "order_reference_id": self.reference,
            "order_number": ref[0],
            "total_amount": 
            {

                "amount": str(self.amount),
                "currency": self.currency_id.name

            },
            "description": self.reference,
            "country_code": "SA" if self.currency_id.name == "SAR" else "AE",
            "payment_type": "PAY_BY_INSTALMENTS",
            # "instalments": null,
            # "locale": "en_US",
            "items": items,
            "consumer": {
                            "first_name": partner_first_name,
                            "last_name": partner_last_name,
                            "phone_number": self.partner_id.phone,
                            "email": self.partner_id.email[:127],
                        },
            "shipping_address": {
                                "first_name": partner_first_name,
                                "last_name": partner_last_name,
                                "line1": "3764 Al Urubah Rd",
                                "city": self.partner_id.city or self.partner_id.state_id.name or self.partner_id.city_id.name,
                                "country_code": "SA" if self.currency_id.name == "SAR" else "AE",
                                },
            "tax_amount": tax_amount,
            "shipping_amount": {
                                "amount": "0",
                                "currency": self.currency_id.name
            },
            "merchant_url": {
                            "success": success_url,
                            "failure": failure_url,
                            "cancel": cancel_url,
                            "notification": notification_url
                        },
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on Mercado Pago data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'tamara' or len(tx) == 1:
            return tx
        # {'decline_type': 'soft decline',
        # 'orderId': '475ae32f-c049-496a-950d-a5691730cd57',
        # 'paymentStatus': 'declined'
        # paymentStatus}
        orderId = notification_data.get('orderId')
        paymentStatus = notification_data.get('paymentStatus')
        
        if not orderId:
            raise ValidationError("Tamara: " + _("Received data with missing reference."))

        tx = self.search([('tamara_order_id', '=', orderId), ('provider_code', '=', 'tamara')])
        if not tx:
            raise ValidationError(
                "Tamara: " + _("No transaction found matching reference %s.", reference)
            )
        return tx
    def _send_refund_request(self, amount_to_refund=None):
        """ Override of `payment` to send a refund request to Tamara.

        Note: self.ensure_one()

        :param float amount_to_refund: The amount to refund.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'tamara':
            return refund_tx

        # Make the refund request to Razorpay.

        payload = {
            "order_id": refund_tx.source_transaction_id.tamara_order_id,
            "refunds": [
                    {
                        "capture_id": refund_tx.source_transaction_id.tamara_capture_id,
                        "total_amount": {
                                        "amount": str(-refund_tx.amount,),
                                        "currency": refund_tx.currency_id.name
                        }
                        
                    }
            ]
        }
        _logger.info(
            "Payload of '/payments/refund' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(payload)
        )
        response_content = refund_tx.provider_id._tamara_make_request(
            f'payments/refund', payload=payload
        )
        _logger.info(
            "Response of '/payments/refund' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(response_content)
        )
        refund_id = response_content.get('refunds')[0].get('refund_id')
        if not refund_id:
            raise ValidationError("Tamara: " + _("Received data with missing refund ID."))
        self.tamara_refund_id = refund_id
        status = response_content.get('status', False)
        self.tamara_status = status
        refund_tx.tamara_refund_id = refund_id
        refund_tx._set_done()

        return refund_tx
    
    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Tamara data.

        Note: self.ensure_one() from `_process_notification_data`

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'tamara':
            return

        orderId = notification_data.get('orderId')
        payment_status = notification_data.get('paymentStatus', False)
        cancel_id = notification_data.get('cancel_id', False)
        if not orderId:
            raise ValidationError("Tamara: " + _("Received data with missing Order ID."))
        # self.provider_reference = payment_id
        if self.operation == 'refund':
                self.env.ref('payment.cron_post_process_payment_tx')._trigger()
        if payment_status == 'declined':
            decline_type = notification_data.get('decline_type')
        if payment_status == 'approved':
            # Authorise the order
            verified_payment_data = self.provider_id._tamara_make_request(
                f'/orders/{orderId}/authorise', method='POST'
            )
            self.tamara_capture_id = verified_payment_data.get('capture_id')
            self.tamara_status = verified_payment_data.get('status')
            payment_status = verified_payment_data.get('status')
            
# {'order_id': '54e1ba32-4148-4e7c-af61-2b7224bfa9fd', 
#  'status': 'fully_captured',
#  'order_expiry_time': '2022-12-20T07:50:09+00:00',
#  'payment_type': 'PAY_BY_INSTALMENTS',
#  'auto_captured': True,
#  'authorized_amount': {'amount': 287.5, 'currency': 'SAR'}, 'capture_id': '38365ce4-98eb-4db2-84b0-c1eec905d7a1'
# 
# 'paymentStatus': 'canceled',
#  'stage': 'Payment_error'}

        
        if not payment_status and not cancel_id:
            raise ValidationError("Tamara Pago: " + _("Received data with missing status."))

        if payment_status in TRANSACTION_STATUS_MAPPING['pending']:
            self._set_pending()
        if payment_status in TRANSACTION_STATUS_MAPPING['authorised']:
            self._set_authorized()
        elif payment_status in TRANSACTION_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in TRANSACTION_STATUS_MAPPING['canceled']:
            stage = notification_data.get('stage', ' ')
            decline_type = notification_data.get('decline_type', ' ')
            message = "Tamara: " + _("Payment was canceled. Stage: %s, Decline Type: %s", stage, decline_type)
            self._set_canceled(message)
        else:  # Classify unsupported payment status as the `error` tx state.
            _logger.warning(
                "Received data for transaction with reference %s with invalid payment status: %s",
                self.reference, payment_status
            )
            self._set_error(
                "Tamara: " + _("Received data with invalid status: %s", payment_status)
            )
