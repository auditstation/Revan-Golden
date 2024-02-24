# -*- coding: utf-8 -*-
{
    'name': "Print details",
    'sequence': 10,
    'version': '16.0.0',
    'depends': [
        'base','portal','sale'
    ],

    'data': [
        'views/print_details.xml',


    ],
    'assets': {
        'web.assets_frontend': [
            'portal_edits/static/scss/main.css',
        ]
    },

    'application': True,
}
