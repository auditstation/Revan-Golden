import base64
import json
import secrets
import string
import logging
from werkzeug import urls
from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import api, fields, models


from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

import werkzeug
from werkzeug.urls import url_encode
import os
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS



import odoo
import odoo.modules.registry
from odoo import http
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url, is_user_internal



_logger = logging.getLogger(__name__)

class UserInherit(models.Model):
    _inherit="res.users"
    tel_pass = fields.Char(groups='base.group_no_one',invisible=True, copy=False)
    def random_password(length=40, prefix="pass"):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(20))
        return password
    def change_user_pass(self):
        for rec in self:
            if rec.share:
                passw = rec.random_password()

                
                rec.sudo().write({'password':passw,'tel_pass':passw})
            else:
                rec.sudo().write({'login':rec.partner_id.phone})

class PortalInherit(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone", "state_id", "country_id", "street"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "city", "email", "vat", "company_name", "didication_letter"]
    def details_form_validate(self, data, partner_creation=False):
        
        
        error = dict()
        error_message = []
        error, error_message = super().details_form_validate(data)
        if data.get('phone') and data.get('country_id'):
            prefix_code="".join(str(request.env['res.country'].browse(int(data.get('country_id'))).phone_code).split())
            phone_limit=request.env['res.country'].browse(int(data.get('country_id'))).phone_limit 
            data_phone = "".join(data.get('phone').split())
           
            if data_phone[0:4]!= '+'+ prefix_code and data_phone[0:5]!= '00'+ prefix_code: 
                
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
           
               
            elif  data_phone[1:4] == prefix_code and len((data_phone[4:]))!=phone_limit:
               
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
            elif data_phone[0:2] =='00' and data_phone[2:5] == prefix_code and len((data_phone[5:]))!=phone_limit: 
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
        return error, error_message


class WebsitePortalsInherit(WebsiteSale):
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
        req = ["name", "country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = ["name", "country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        error, error_message = super().checkout_form_validate(mode, all_form_values, data)   
        if data.get('phone') and data.get('country_id'):
            prefix_code="".join(str(request.env['res.country'].browse(int(data.get('country_id'))).phone_code).split())
            phone_limit=request.env['res.country'].browse(int(data.get('country_id'))).phone_limit 
            data_phone = "".join(data.get('phone').split())
           
            if data_phone[:1]!= '+' and data_phone[0:2]!= '00':  
                
                
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
           
               
            elif  data_phone[1:4] == prefix_code and len((data_phone[4:]))!=phone_limit:
               
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
            elif data_phone[0:2] =='00' and data_phone[2:5] == prefix_code and len((data_phone[5:]))!=phone_limit: 
                error["phone"] = 'error'
                error_message.append(_('Invalid number! Please enter a valid number with country code %s',str("+"+prefix_code)))
        return error, error_message

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
    
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
    
        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}
        
        partner_id = int(kw.get('partner_id', -1))
      
        
    
        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
           
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')
    
        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":
            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
          

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # if 'country_id' in kw:
                #     prefix_code=str(request.env['res.country'].sudo().browse(int(kw['country_id'])).phone_code)
                #     partner_object = request.env['res.partner'].sudo().browse(partner_id)
                #     if partner_object.phone[0:4]!= '+'+ prefix_code and partner_object.phone[0:5]!= '00'+ prefix_code:
                #         partner_object.phone =  '+'+prefix_code + partner_object.phone
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                 mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                    # We need to update the pricelist(by the one selected by the customer), because onchange_partner reset it
                    # We only need to update the pricelist when it is not redirected to /confirm_order
                    if kw.get('callback', '') != '/shop/confirm_order':
                        request.website.sale_get_order(update_pricelist=True)
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id
                    
    
                # TDE FIXME: don't ever do this
                # -> TDE: you are the guy that did what we should never do in commit e6f038a
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
        
                
                if 'didication_letter' in kw:
                    order.partner_shipping_id.didication_letter = kw['didication_letter']
            
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')
    
            
            
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'account_on_checkout': request.website.account_on_checkout,
            'is_public_user': request.website.is_public_user()
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        _logger.info("Starting confirm_order route")

        # Get the current order
        order = request.website.sale_get_order()
        if not order:
            _logger.warning("No active sale order found")
            return request.redirect("/shop/cart")

        _logger.info(f"Order found: {order.name}, ID: {order.id}")

        # Check and update the pricelist if needed
        try:
            if order.partner_shipping_id.country_id.currency_id.id != order.pricelist_id.currency_id.id:
                _logger.info("Updating pricelist based on shipping country currency")

                # Find the new pricelist
                new_pricelist = request.env['product.pricelist'].sudo().search([
                    ('currency_id', '=', order.partner_shipping_id.country_id.currency_id.id)
                ], limit=1)

                if new_pricelist:
                    order.pricelist_id = new_pricelist.id
                    _logger.info(f"Pricelist updated to: {new_pricelist.name}")

                order.sudo().action_update_prices()

                # Process each order line for services
                for rec in order.order_line.filtered(
                        lambda act: act.product_template_id.product_variant_id.detailed_type == 'service'):
                    _logger.info(f"Processing service product: {rec.product_template_id.name}")

                    # Check currency and update product if needed
                    if rec.order_id.pricelist_id.currency_id.name != 'OMR':
                        _logger.info("Currency is not OMR, updating delivery product")

                        prd = request.env['delivery.carrier'].sudo().search([
                            ('country_ids', 'in', [order.partner_shipping_id.country_id.id])
                        ]).product_id.product_tmpl_id.id

                        if prd:
                            _logger.info(f"New product template ID for delivery: {prd}")
                            rec.product_template_id = prd

                        # Rate shipment and set delivery line
                        res = rec.order_id.carrier_id.rate_shipment(rec.order_id)
                        _logger.info(f"Shipment rate response: {res}")

                        care = request.env['delivery.carrier'].sudo().search([
                            ('product_id', '=', rec.product_template_id.product_variant_id.id)
                        ])

                        if care and res:
                            rec.order_id.set_delivery_line(care, res['price'])
                            _logger.info(f"Delivery line set with carrier {care.name} and price {res['price']}")
                    else:
                        _logger.info("Currency is OMR, removing service line")
                        rec.unlink()
        except Exception as e:
            _logger.error(f"Error while processing order lines: {str(e)}", exc_info=True)

        # Check if any redirection is needed
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            _logger.info("Redirection triggered")
            return redirection

        # Update taxes and session
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        _logger.info(f"Order taxes computed and session updated with order ID {order.id}")

        # Check if the extra info step is active
        extra_step = request.website.viewref('website_sale.extra_info')
        if extra_step.active:
            _logger.info("Extra info step is active, redirecting to /shop/extra_info")
            return request.redirect("/shop/extra_info")

        _logger.info("Redirecting to /shop/payment")
        return request.redirect("/shop/payment")
    # @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    # def shop_payment(self, **post):
    #     order = request.website.sale_get_order()
    #     if order.partner_shipping_id.country_id.currency_id.id != order.pricelist_id.currency_id.id:
    #
    #        order.pricelist_id = request.env['product.pricelist'].sudo().search([('currency_id','=',order.partner_shipping_id.country_id.currency_id.id)]).id
    #        order.sudo().action_update_prices()
    #        for rec in order.order_line.filtered(lambda act: act.product_template_id.product_variant_id.detailed_type == 'service'):
    #             if rec.order_id.pricelist_id.currency_id.name!='OMR':
    #                 _logger.info(f'aaaaaaaaaaaaaaaaaaaaaaa{rec.product_template_id.name}')
    #                 prd= request.env['delivery.carrier'].sudo().search([('country_ids','in',[order.partner_shipping_id.country_id.id])]).product_id.product_tmpl_id.id
    #
    #                 rec.product_template_id = prd
    #                 res = rec.order_id.carrier_id.rate_shipment(rec.order_id)
    #                 care= request.env['delivery.carrier'].sudo().search([('product_id','=',rec.product_template_id.product_variant_id.id)])
    #                 rec.order_id.set_delivery_line(care,res['price'])
    #             else:
    #                 rec.unlink()
    #     redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
    #     if redirection:
    #         return redirection
    #
    #     render_values = self._get_shop_payment_values(order, **post)
    #     render_values['only_services'] = order and order.only_services or False
    #
    #     if render_values['errors']:
    #         render_values.pop('providers', '')
    #         render_values.pop('tokens', '')
    #
    #     return request.render("website_sale.payment", render_values)

    

class CountryInherit(models.Model):
    _inherit = "res.country"
    active = fields.Boolean('Active', default=True)
   
    phone_limit = fields.Integer('Limit Phone')

class PartnerInherit(models.Model):
    _inherit = "res.partner"
    didication_letter = fields.Text('Didication letter')


class AccountInherit(models.Model):
    _inherit = "account.move"
    didication_invoice = fields.Text('Didication letter')


class SaleInherit(models.Model):
    _inherit = "sale.order"
    didication_sale = fields.Text('Didication letter')


class WebsiteInherit(models.Model):
    _inherit = "website"

    def sale_get_order(self, *args, **kwargs):
        so = super().sale_get_order(*args, **kwargs)
        
        if so.partner_shipping_id.didication_letter:
            so.didication_sale = so.partner_shipping_id.didication_letter
            so.partner_shipping_id.didication_letter = ''
        return so


class InheritLogin(AuthSignupHome):

    
    @http.route()
    def web_login(self, *args, **kw):
        
        ensure_db()
        user=request.env['res.users'].sudo().search([('login','=',kw.get('login'))])
        passw = self.random_password()
        if user:
            if user.tel_pass and user.share:
              

                kw['password'] =user.tel_pass
                request.params["password"] = user.tel_pass
                
               
                
            elif not user.share:
                
               
                if 'password' in kw:
                    request.params["password"] = kw['password']
                else:
                    request.params["password"] = ''
                    return request.render('web.login',{'error':'you should fill password'})
        elif not user and kw.get('login'):   
            request.params["password"] = ''
            return request.redirect('/web/signup')
        
       
        response = super().web_login(*args, **kw)
       
        
        response.qcontext.update(self.get_auth_signup_config())
        if request.session.uid:
            if request.httprequest.method == 'GET' and request.params.get('redirect'):
                # Redirect if already logged in and redirect param is present
                return request.redirect(request.params.get('redirect'))
            # Add message for non-internal user account without redirect if account was just created
            if response.location == '/web/login_successful' and kw.get('confirm_password'):
                return request.redirect_query('/web/login_successful', query={'account_created': True})
       
        return response
    
    def changed_pass(self,user,passw):
       
        request.env['res.users'].with_user(SUPERUSER_ID).browse(user)._change_password(passw)
        request.env['res.users'].with_user(SUPERUSER_ID).browse(user).write({'password':passw})

    def random_password(length=40, prefix="pass"):
        
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(20))
        return password
    
    @http.route()
    def web_auth_signup(self, *args, **kw):
        passw = self.random_password()
        if 'password' in kw:
            kw['password'] = passw
            kw['confirm_password'] = passw
            request.params["password"] = passw
            request.params["confirm_password"] = passw
        response = super().web_auth_signup(*args, **kw)
        user=request.env["res.users"].sudo().search([("login", "=", kw.get("login"))])
        user.tel_pass = passw
        phone=kw.get("login")
        user.partner_id.mobile =  phone
        user.partner_id.phone = kw.get("login")
        user.partner_id.email = ''
        return response


    

    
