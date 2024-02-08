# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCountryState(models.Model):
    _inherit = "res.country.state"

    name = fields.Char(string='State Name', required=True, translate=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')