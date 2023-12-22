# -*- coding: utf-8 -*-
{
    'name': "custom_website_pricelist",

    'summary': """This module is responsible for modifying the navbar view on mobile devices in the website module.""",

    'description': """
        This module gives you the option to select the currency of different countries through a view.xml
       which contains a selector type input with different currencies.
    """,

    'author': "OSM Software",
    'website': "https://www.osm-soft.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website_sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale', 'website_custom_code'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/custom_navbar.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_website_pricelist/static/src/scss/main.css',
        ]
    },
}
