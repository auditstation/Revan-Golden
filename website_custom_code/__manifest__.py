# -*- coding: utf-8 -*-
{
    'name': "Website Custom Code",

    'summary': """
        Show flag on currency Hide Unavailable Variants on the website""",
    'description': """ This module gives option to hide the variants form the website by simply enabling a
    boolean field. Here no need to set the exclusions. So customer can only see the valid and available attribute 
    values for the product.
    Hide Variants,
    Hide Attribute Values,
    Odoo Hide Variants,
    Hide Product Variants """,

    'sequence': 50,
    'author': "Mindrich Technologies Pvt. Ltd.",
    'company': 'Mindrich Technologies Pvt. Ltd.',
    'category': 'eCommerce',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale'],

    # always loaded
    'data': [
        'views/product_view.xml',
        'views/price_list_template.xml',
        'views/res_currency_view.xml',
        'views/custom_navbar.xml',
        'views/hide_variant.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 'website_custom_code/static/src/scss/main.css',
            # 'website_custom_code/static/src/js/hide.js',
        ]
    },
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
}
