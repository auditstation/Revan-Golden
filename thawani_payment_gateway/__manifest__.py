
{
    'name': 'THawani Payment Gateway',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 50,
    'version': '16.0.1.0.0',
    'description': """Thawani Payment Gateway""",
    'Summary': """Payment Provider : Thawani """,
    'author': "Hassan ",
    'company': 'Hassan',
    'maintainer': 'Hassan',
    'website': "",
    'depends': ['payment','account','website','website_sale'],
    'data': [
        'views/payment_template.xml',
        'views/payment_myfatoorah_templates.xml',
        'views/myfatoorah_payment_template.xml',
        'data/payment_provider_data.xml',

    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
