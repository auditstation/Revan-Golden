

import logging
import pprint

import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_tamara.const import SUPPORTED_CURRENCIES


_logger = logging.getLogger(__name__)


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    
    code = fields.Selection(
        selection_add=[('tamara', "Tamara")], ondelete={'tamara': 'set default'}
    )
    tamara_api_token = fields.Char(
        string="Tamara Access Token",
        required_if_provider='mercado_pago',
        groups='base.group_system',
    )
    tamara_notification_token = fields.Char(
        string="Tamara Notification Token",
        required_if_provider='mercado_pago',
        groups='base.group_system',
    )
    def _compute_feature_support_fields(self):
        
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'tamara').update({
            'support_fees': False,
            'support_manual_capture': False,
            'support_refund': 'partial',
            'support_tokenization': False,
        })

    # === BUSINESS METHODS === #

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of `payment` to unlist Tamara providers for unsupported currencies. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in SUPPORTED_CURRENCIES:
            providers = providers.filtered(lambda p: p.code != 'tamara')

        return providers

    def _tamara_make_request(self, endpoint, payload=None, method='POST'):
        """ Make a request to Mercado Pago API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        self.ensure_one()
        api_base_url = "https://api-sandbox.tamara.co" if self.state == 'test' else "https://api.tamara.co"
        url = urls.url_join(api_base_url, endpoint)
        headers = {'Authorization': f'Bearer {self.tamara_api_token}'}
        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    _logger.exception(
                        "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                    )
                    response_content = response.json()
                    error_code = response_content.get('errors')[0].get('error_code')
                    error_message = response_content.get('message')
                    raise ValidationError("Tamara: " + _(
                        "The communication with the API failed. Tamara gave us the following "
                        "information: '%s' (code %s)", error_message, error_code
                    ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Tamara Pago: " + _("Could not establish the connection to the API.")
            )
        return response.json()
