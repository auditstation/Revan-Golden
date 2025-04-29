import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        _logger.info("Starting custom _run_pull logic")
        new_procurements = []

        for procurement, rule in procurements:
            product = procurement.product_id
            needed_qty = procurement.product_qty
            _logger.info(f"Processing procurement for product: {product.display_name}, Requested Qty: {needed_qty}")

            # Get locations
            khoud_loc = self.env['stock.location'].search([('name', '=', 'khoud/Stock')], limit=1)
            bawshar_loc = self.env['stock.location'].search([('name', '=', 'bawshar/Stock')], limit=1)

            _logger.info(f"Khoud location found: {khoud_loc.name if khoud_loc else 'Not Found'}")
            _logger.info(f"Bawshar location found: {bawshar_loc.name if bawshar_loc else 'Not Found'}")

            if not khoud_loc or not bawshar_loc:
                _logger.warning("One or both locations not found. Falling back to default behavior.")
                return super()._run_pull([(procurement, rule)])

            available_in_khoud = product.with_context(location=khoud_loc.id).qty_available
            _logger.info(f"Available in Khoud: {available_in_khoud} units")

            # If khoud has enough stock, use default pull
            if available_in_khoud >= needed_qty:
                _logger.info("Khoud has enough stock. Using default pull.")
                return super()._run_pull([(procurement, rule)])

            # If khoud has partial stock, create a partial procurement
            remaining_qty = needed_qty
            if available_in_khoud > 0:
                _logger.info(f"Khoud can partially fulfill: {available_in_khoud} units. Creating partial procurement.")
                partial_procurement = procurement.copy({
                    'product_qty': available_in_khoud,
                })
                new_procurements.append((partial_procurement, rule))
                remaining_qty = needed_qty - available_in_khoud
                _logger.info(f"Remaining quantity to pull from Bawshar: {remaining_qty}")

            # Create internal transfer move from Bawshar to Khoud for the remaining quantity
            if remaining_qty > 0 and bawshar_loc:
                move_vals = rule._prepare_move_values(
                    procurement.product_id,
                    remaining_qty,
                    procurement.product_uom,
                    bawshar_loc,
                    khoud_loc,
                    procurement.values,
                    procurement.origin
                )
                self.env['stock.move'].create(move_vals)
                _logger.info(f"Created stock move from Bawshar to Khoud for: {remaining_qty} units")

        if new_procurements:
            _logger.info("Running default pull for partial procurements.")
            return super()._run_pull(new_procurements)

        _logger.info("No partial procurements. Running default pull for original procurements.")
        return super()._run_pull(procurements)
