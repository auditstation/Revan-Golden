from odoo import models,fields
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template.attribute.value"

    def _only_active_website(self):
        _logger.info("############### INSIDE _only_active_website: ")

        def has_stock(ptav):
            _logger.info("############### INSIDE has_stock: ")

            available_stock = 0
            for variant in ptav.ptav_product_variant_ids:
                available_stock += variant.qty_available
                _logger.info(f"############### available_stock: {available_stock}")

            return available_stock > 0

        return self.sudo().filtered(lambda ptav: ptav.ptav_active and has_stock(ptav))


