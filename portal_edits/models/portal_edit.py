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

class WebsitePortalsInherit(WebsiteSale):
    WRITABLE_PARTNER_FIELDS = [
        'name',
        'email',
        'phone',
        'state_id',
        'didication_letter'
    ]

   
        """ Create or update a partner

        To create a partner, this controller usually calls `values_preprocess()`, then
        `checkout_form_validate()`, then `values_postprocess()` and finally `_checkout_form_save()`.
        Since these methods are very specific to the checkout form, this method makes it possible to
        create  a partner for more specific flows like express payment, which does not require all
        the checks carried out by the previous methods. Parts of code in this method come from those.

        :param dict partner_details: The values needed to create the partner or to edit the partner.
        :param bool edit: Whether edit an existing partner or create one, defaults to False.
        :param dict custom_values: Optional custom values for the creation or edition.
        :return int: The id of the partner created or edited
        """
        values = self.values_preprocess(partner_details)
        _logger.info(f'dsssasasa{values}')

        # Ensure that we won't write on unallowed fields.
        sanitized_values = {
            k: v for k, v in values.items() if k in self.WRITABLE_PARTNER_FIELDS
        }
        sanitized_custom_values = {
            k: v for k, v in custom_values.items()
            if k in self.WRITABLE_PARTNER_FIELDS + ['partner_id', 'parent_id', 'type']
        }
        _logger.info(f'sssssssssssss{sanitized_custom_values}')

        if request.website.specific_user_account:
            sanitized_values['website_id'] = request.website.id

        lang = request.lang.code if request.lang.code in request.website.mapped(
            'language_ids.code'
        ) else None
        if lang:
            sanitized_values['lang'] = lang

        partner_id = sanitized_custom_values.get('partner_id')
        if edit and partner_id:
            request.env['res.partner'].browse(partner_id).sudo().write(sanitized_values)
        else:
            sanitized_values = dict(sanitized_values, **{
                'company_id': request.website.company_id.id,
                'team_id': request.website.salesteam_id and request.website.salesteam_id.id,
                'user_id': request.website.salesperson_id.id,
                **sanitized_custom_values
            })
            partner_id = request.env['res.partner'].sudo().with_context(
                tracking_disable=True
            ).create(sanitized_values).id
        return partner_id
    def _get_mandatory_fields_billing(self, country_id=False):
        _logger.info(f'sssssssssssss')
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