# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo import http
from odoo.http import request

class ResCountryState(models.Model):
    _inherit = "res.country.state"

    name = fields.Char(string='State Name', required=True, translate=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')



class CustomHomeController(http.Controller):

    @http.route('/my/home', type='http', auth='user', website=True)
    def custom_home(self, **kwargs):
        # Add your custom logic here
        user = request.env.user
        # values = {
        #     'user_name': user.name,
        #     'custom_message': "Welcome to the custom home page!",
        # }
        return request.render('portal.portal_my_home')
