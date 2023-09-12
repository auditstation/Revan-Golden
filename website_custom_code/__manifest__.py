{
    'name': 'Website Custom Code',
    'category': 'Website',
    'sequence': 50,
    'version': '16.0.1.0.0',
    'description': """Website Custom Code""",
    'Summary': """Website Custom Code""",
    'author': "Mindrich Technologies Pvt. Ltd.",
    'company': 'Mindrich Technologies Pvt. Ltd.',
    'maintainer': 'Hassan',
    'website': "",
    'depends': ['website', 'website_sale'],
    'data': [
        'views/website_sale_inherit.xml',
        'views/res_currency_view.xml',
        'views/price_list_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_custom_code/static/src/scss/main.scss',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
