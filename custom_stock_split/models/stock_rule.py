from odoo import models, fields, api
from odoo.exceptions import UserError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        new_procurements = []
        for procurement, rule in procurements:
            product = procurement.product_id
            needed_qty = procurement.product_qty
            # khoud_loc = self.env.ref('stock.stock_location_stock')  # Replace with khoud location XML ID
            khoud_loc = self.env['stock.location'].search([('name', '=', 'khoud/Stock')], limit=1)
            bawshar_loc = self.env['stock.location'].search([('name', '=', 'bawshar/Stock')], limit=1)

            available_qty = product.with_context(location=khoud_loc.id).qty_available

            if available_qty >= needed_qty:
                return super()._run_pull([(procurement, rule)])

            # Create partial move from khoud
            if available_qty > 0:
                partial_proc = procurement.copy({
                    'product_qty': available_qty,
                })
                new_procurements.append((partial_proc, rule))

            # Create remaining move from bawshar to khoud
            remaining_qty = needed_qty - available_qty
            if bawshar_loc:
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
            return super()._run_pull(new_procurements)

        return super()._run_pull(procurements)
