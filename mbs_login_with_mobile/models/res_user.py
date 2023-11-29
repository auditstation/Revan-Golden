from odoo import api, fields, models, tools, _


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_login_domain(self, login):
        return ['|', ('login', '=', login), ('mobile', '=', login)]