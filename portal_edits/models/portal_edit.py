import base64
import json
import math
import re

from werkzeug import urls

from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)
class PortalInherit(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone","state_id","country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode","city","street","email","vat", "company_name"]

class WebsitePortalInherit(WebsiteSale):
    def _get_mandatory_fields_billing(self, country_id=False):
        req = ["name","country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req
    def _get_mandatory_fields_shipping(self, country_id=False):
        req = ["name","country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req    
  
