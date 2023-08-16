#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import logging

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class PaymentTxmpgs(models.Model):
    _inherit = 'payment.transaction'

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on data.

        Note: self.ensure_one()

        :param dict data: The feedback data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "mpgs":
            return
        self._set_done()
        self.with_context({'mpgs': True})._reconcile_after_done()

    def _reconcile_after_done(self):
        """ Override of payment to automatically confirm quotations and generate invoices. """
        if self._context.get('mpgs'):
            sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
            for tx in self:
                tx._check_amount_and_confirm_order()
            # send order confirmation mail
            sales_orders._send_order_confirmation_mail()
            # invoice the sale orders if needed
            self._invoice_sale_orders()
            if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice') and any(
                    so.state in ('sale', 'done') for so in self.sale_order_ids):
                default_template = self.env['ir.config_parameter'].sudo().get_param(
                    'sale.default_invoice_email_template')
                if default_template:
                    for trans in self.filtered(
                            lambda t: t.sale_order_ids.filtered(lambda so: so.state in ('sale', 'done'))):
                        trans = trans.with_company(trans.provider_id.company_id).with_context(
                            mark_invoice_as_sent=True,
                            company_id=trans.provider_id.company_id,
                        )
                        for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                            invoice.message_post_with_template(int(default_template),
                                                               email_layout_xmlid="mail.mail_notification_light")
                self.invoice_ids.filtered(lambda inv: inv.state == 'draft').action_post()

                # Create and post missing payments for transactions requiring reconciliation
                for tx in self.filtered(lambda t: t.operation != 'validation' and not t.payment_id):
                    tx._create_payment()
        else:
            return super()._reconcile_after_done()
