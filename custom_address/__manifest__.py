# -*- coding: utf-8 -*-
{
    'name': "custom_address - Website_Sales",

    'summary': """ Country Address Selector Customization """,

    'description': """
       This custom module adjusts the list of countries available in an address selector field, 
       limiting it to displaying only five specific countries.
    """,

    'author': "OSM Software",
    'website': "https://www.osm-soft.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website_sale',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}
