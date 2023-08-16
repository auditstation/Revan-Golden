

import logging
import pprint

import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_tamara.const import SUPPORTED_CURRENCIES


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # override as you can void tamara transcation
    @api.depends('transaction_ids')
    def _compute_authorized_transaction_ids(self):
        for invoice in self:
            invoice.authorized_transaction_ids = invoice.transaction_ids.filtered(
                lambda tx: tx.state == 'authorized' or (tx.state == 'done' and tx.provider_id.code == 'tamara')
            )
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # override as you can void tamara transcation
    @api.depends('transaction_ids')
    def _compute_authorized_transaction_ids(self):
        for invoice in self:
            invoice.authorized_transaction_ids = invoice.transaction_ids.filtered(
                lambda tx: tx.state == 'authorized' or (tx.state == 'done' and tx.provider_id.code == 'tamara')
            )