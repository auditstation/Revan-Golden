from odoo import fields, models


class ResCurrencyInherit(models.Model):
    _inherit = 'res.currency'

    flag_image = fields.Binary('Flag')


class ProductPriceListInherit(models.Model):
    _inherit = 'product.pricelist'

    flag_image = fields.Binary(related='currency_id.flag_image')
