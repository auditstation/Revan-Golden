# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCountryState(models.Model):
    _inherit = "res.country.state"

    name = fields.Char(string='State Name', required=True, translate=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')






from odoo import http
from odoo.http import request

class CustomHomeController(http.Controller):

    @http.route('/my/home', type='http', auth='user', website=True)
    def custom_home(self, **kwargs):
        # Add your custom logic here
        user = request.env.user
        # values = {
        #     'user_name': user.name,
        #     'custom_message': "Welcome to the custom home page!",
        # }
        return request.render('wt_revan_golden_website.portal_my_home')
