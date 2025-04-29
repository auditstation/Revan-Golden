import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        _logger.info("Running custom _run_pull for custom stock allocation logic")
        new_procurements = []

        for procurement, rule in procurements:
            product = procurement.product_id
            needed_qty = procurement.product_qty
            _logger.info(f"Procurement: {product.display_name}, Needed Qty: {needed_qty}")

            # Locations
            khoud_loc = self.env['stock.location'].search([('id', '=', 8)], limit=1)
            bawshar_loc = self.env['stock.location'].search([('id', '=', 18)], limit=1)

            if not khoud_loc or not bawshar_loc:
                _logger.warning("Required stock locations not found, using default behavior.")
                return super()._run_pull([(procurement, rule)])

            available_in_khoud = product.with_context(location=khoud_loc.id).qty_available
            _logger.info(f"Available in Khoud: {available_in_khoud}")

            if available_in_khoud >= needed_qty:
                _logger.info("Khoud has enough stock, using default pull.")
                return super()._run_pull([(procurement, rule)])

            # Remaining qty after pulling from khoud
            remaining_qty = needed_qty
            if available_in_khoud > 0:
                partial_proc_vals = {
                    'name': procurement.name,
                    'product_id': procurement.product_id,
                    'product_qty': available_in_khoud,
                    'product_uom': procurement.product_uom,
                    'location_id': procurement.location_id.id,
                    'rule_id': rule.id,
                    'group_id': procurement.group_id.id,
                    'date_planned': procurement.date_planned,
                    'values': procurement.values,
                    'origin': procurement.origin,
                }
                _logger.info(f"Creating partial procurement with {available_in_khoud} units from Khoud")
                new_procurements.append((self.env['procurement.group'].Procurement(**partial_proc_vals), rule))
                remaining_qty -= available_in_khoud

            # Internal transfer from Bawshar to Khoud
            if remaining_qty > 0:
                _logger.info(f"Creating stock move from Bawshar to Khoud for {remaining_qty} units")
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

        if new_procurements:
            _logger.info(f"Running default pull for {len(new_procurements)} partial procurements")
            return super()._run_pull(new_procurements)

        _logger.info("Falling back to default behavior for remaining procurements")
        return super()._run_pull(procurements)
