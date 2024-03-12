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
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)
class PortalInherit(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone","state_id","country_id","street"]
    OPTIONAL_BILLING_FIELDS = ["zipcode","city","email","vat", "company_name","didication_letter"]

class WebsitePortalInherit(WebsiteSale):
    WRITABLE_PARTNER_FIELDS = [
        'name',
        'email',
        'phone',
        'street',
        'street2',
        'city',
        'zip',
        'country_id',
        'state_id',
        'didication_letter'
    ]
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
  
class CountryInherit(models.Model):
    _inherit ="res.country"
    active = fields.Boolean('Active', default=True)

class PartnerInherit(models.Model):
    _inherit ="res.partner"
    didication_letter = fields.Text('Didication letter')    