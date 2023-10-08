# -*- coding: utf-8 -*-
{
    'name': 'Car Rental Management',
    'version': '1.0',
    'summary': 'Car Rental Management Software',
    'description': 'Car Rental Management Software for tracking rented cars and fines.',
    'category': 'Services',
    'author': 'Your Name',
    'website': 'https://www.odoomates.tech',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/car_rental_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
