import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        _logger.info("Custom _run_pull triggered with %d procurements", len(procurements))
        new_procurements = []

        for procurement, rule in procurements:
            product = procurement.product_id
            needed_qty = procurement.product_qty
            _logger.info(f"Processing product: {product.display_name}, Needed: {needed_qty}")

            khoud_loc = self.env['stock.location'].search([('id', '=', 8)], limit=1)
            bawshar_loc = self.env['stock.location'].search([('id', '=', 18)], limit=1)

            if not khoud_loc or not bawshar_loc:
                _logger.warning("Stock locations not found. Default Odoo behavior will run.")
                return super()._run_pull([(procurement, rule)])

            available_in_khoud = product.with_context(location=khoud_loc.id).qty_available
            _logger.info(f"Available in Khoud: {available_in_khoud}")

            remaining_qty = needed_qty
            if available_in_khoud >= needed_qty:
                _logger.info("Enough stock in Khoud. Running normal pull.")
                return super()._run_pull([(procurement, rule)])

            # Partial procurement from Khoud
            if available_in_khoud > 0:
                _logger.info(f"Creating procurement for {available_in_khoud} from Khoud")

                # Safely handle the 'group_id' attribute
                group_id = getattr(procurement, 'group_id', None)  # Safely get group_id
                if group_id:
                    group_id = group_id.id
                else:
                    group_id = False

                new_proc = self.env['procurement.group'].create({
                    'product_id': procurement.product_id.id,
                    'product_qty': available_in_khoud,
                    'product_uom': procurement.product_uom.id,
                    'location_id': procurement.location_id.id,
                    'name': procurement.name,
                    'origin': procurement.origin,
                    'company_id': procurement.company_id.id,
                    'group_id': group_id,  # Use group_id if exists, otherwise False
                })
                new_procurements.append((new_proc, rule))
                remaining_qty -= available_in_khoud

            # Internal transfer from Bawshar to Khoud
            if remaining_qty > 0:
                _logger.info(f"Creating internal transfer from Bawshar to Khoud for {remaining_qty}")
                move_vals = {
                    'name': procurement.name,
                    'company_id': procurement.company_id.id,
                    'product_id': procurement.product_id.id,
                    'product_uom_qty': remaining_qty,
                    'product_uom': procurement.product_uom.id,
                    'location_id': bawshar_loc.id,
                    'location_dest_id': khoud_loc.id,
                    'procure_method': 'make_to_stock',
                    'group_id': group_id,  # Safely handle group_id here as well
                    'origin': procurement.origin,
                }

                self.env['stock.move'].create(move_vals)

        if new_procurements:
            _logger.info(f"Running default pull for {len(new_procurements)} new procurements")
            return super()._run_pull(new_procurements)

        _logger.info("No custom action taken. Default pull running.")
        return super()._run_pull(procurements)
