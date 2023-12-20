from odoo import models, fields, api


class Country(models.Model):
    _inherit = 'res.country'
    active = fields.Boolean(string="active", default=False)
