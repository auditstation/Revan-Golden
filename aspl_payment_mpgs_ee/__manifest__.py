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

{
    'name': 'Mastercard Payment Gateway Service(MPGS) Payment Provider (Enterprise) [Nets:Tag]',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Account',
    'description': """Mastercard Payment Gateway Service(MPGS) Payment Provider
    """,
    'website': 'http://www.acespritech.com',
    'price': 60,
    'currency': 'EUR',
    'license': 'LGPL-3',
    'summary': 'Mastercard Payment Gateway Service(MPGS) Payment Provider',
    'depends': ['base', 'website_sale'],
    'external_dependencies': {'python': ['pycountry']},
    'data': [
        'views/payment_mpgs_templates.xml',
        'views/payment_provider.xml',
        'data/payment_provider_data.xml',
    ],
    'images': ['static/description/master_card.jpg'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'https://ap-gateway.mastercard.com/checkout/version/61/checkout.js'
        ],
    },
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
