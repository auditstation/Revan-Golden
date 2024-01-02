from odoo import models,fields

class ProductTemplate(models.Model):
    _inherit = "product.template.attribute.value"

    def _only_active_website(self):
        def has_stock(ptav):
            available_stock = 0
            for variant in ptav.ptav_product_variant_ids:
                available_stock += variant.qty_available
            return available_stock > 0

        return self.filtered(lambda ptav: ptav.ptav_active and has_stock(ptav))


