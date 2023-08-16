# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import pycountry
import requests
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)



class WebsiteSale(WebsiteSale):

    @http.route(['/get_mpgs_data'], type='json', auth="public", website=True)
    def get_mpgs_data(self, **kw):
        res = {}
        mpgs_id = request.env['payment.provider'].sudo().search([('code', '=', 'mpgs')], limit=1)
        tx = request.env['payment.transaction'].sudo().search([], limit=1)
        if tx:
            res['cust_email'] = tx.partner_id.email
            res['cust_phone'] = tx.partner_id.phone
            res['cust_street'] = tx.partner_id.street
            res['cust_city'] = tx.partner_id.city
            res['cust_zip'] = tx.partner_id.zip
            res['cust_state_code'] = tx.partner_id.state_id.name
            if len(tx.partner_id.country_id.code) == 2:
                try:
                    country = pycountry.countries.get(alpha_2=(tx.partner_id.country_id.code).upper())
                    res['cust_country'] = country.alpha_3
                except Exception as e:
                    raise ValueError("Exception-", e)
            else:
                res['cust_country'] = (tx.partner_id.country_id.code).upper()

            res['amount'] = tx.amount
            res['currency'] = tx.currency_id.name

        for sale_order in tx.sale_order_ids:
            for line in sale_order.order_line:
                res['product_name'] = line.product_id.name
                res['order_name'] = tx.reference
                res['order_id'] = tx.id

        """
        According to Country, Bank and merchant details interaction.operation can be change from
        res['interaction.operation'] = 'PURCHASE' or 
        res['interaction.operation'] = 'AUTHORIZE'
        """

        if mpgs_id:
            res['merchant_id'] = mpgs_id.merchant_id
            res['merchant_name'] = mpgs_id.merchant_name
            res['address1'] = mpgs_id.address1
            res['address2'] = mpgs_id.address2
            res['interaction.operation'] = 'PURCHASE'
        # res['interaction.operation'] = 'PURCHASE'
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        cancel_url = base_url + '/shop/payment'
        return_url = base_url + '/shop/completeCallback'
        # res['interaction.cancelUrl'] = cancel_url
        # res['interaction.returnUrl'] = return_url
        # Rest API

        data = [('apiOperation', 'CREATE_CHECKOUT_SESSION'),
                ('apiPassword', mpgs_id.mpgs_secret_key),
                ('apiUsername', 'merchant.' + mpgs_id.merchant_id),
                ('merchant', mpgs_id.merchant_id),
                ('order.id', str(tx.id) + '' + tx.reference),
                ('order.amount', res['amount']),
                ('order.description', tx.reference),
                ('order.currency', res['currency']),
                ('interaction.operation', 'PURCHASE'),
                ('interaction.cancelUrl', cancel_url),
                ('interaction.returnUrl', return_url)
                ]
        
        _logger.warning('nLog: get_mpgs_data ==> data ==> {0}'.format(data))
        '''
        According to country, bank and merchant details mpgs_links can differ
        '''
        if mpgs_id.state == 'enabled':
            # noinspection Pylint
            mpgs_form_url = 'https://ap-gateway.mastercard.com/api/nvp/version/61'
        else:
            mpgs_form_url = 'https://ap-gateway.mastercard.com/api/nvp/version/61'
        f = requests.post(mpgs_form_url, data=data)
        data = str(f.content).split('&')
        for each in data:
            if 'session.id' in each:
                res['session_id'] = each.split('=')[1]
            if 'session.version' in each:
                res['session_version'] = each.split('=')[1]
        return res

    @http.route(['/shop/completeCallback'], type='http', auth="public", website=True)
    def confirm_order_new(self, **post):
        payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
        payment_transaction._process_notification_data(post)
        return request.redirect('/shop/confirmation')
