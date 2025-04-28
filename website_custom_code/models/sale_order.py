import base64
import json
import secrets
import string
import logging
from werkzeug import urls
from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route
from datetime import date
import requests
import io
import datetime
import PyPDF2
import base64


import codecs
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrederInherit(models.Model):
    _inherit = "sale.order"

    def _get_cart_and_free_qty(self, product, line=None):
        """ Get cart quantity and free quantity for given product or line's product.

        Note: self.ensure_one()

        :param ProductProduct product: The product
        :param SaleOrderLine line: The optional line
        """
        self.ensure_one()
        if not line and not product:
            return 0, 0
        cart_qty = sum(self._get_common_product_lines(line, product).mapped('product_uom_qty'))

        # Compute free quantity manually across all internal locations
        prod = product or line.product_id
        internal_quants = prod.stock_quant_ids.filtered(lambda q: q.location_id.usage == 'internal')
        free_qty = sum(internal_quants.mapped('quantity'))

        return cart_qty, free_qty