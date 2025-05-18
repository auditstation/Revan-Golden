from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking,self).button_validate()

        for picking in self:
            if picking.picking_type_id.code == 'internal' and picking.sale_id:
                delivery_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),

                ], order='id ASC')
                if delivery_pickings:
                    # for delivery_picking in delivery_pickings:
                    #     for move in delivery_picking.move_ids_without_package:
                    #         move.quantity  = move.product_uom_qty
                    #     delivery_picking.action_assign()
                    #     delivery_picking.button_validate()

                    for delivery_picking in delivery_pickings:
                        # Only process if there are stock moves to work with
                        if delivery_picking.move_ids_without_package:
                            for move in delivery_picking.move_ids_without_package:
                                move.quantity_done = move.product_uom_qty

                            # Assign stock and validate
                            delivery_picking.action_assign()
                            delivery_picking.button_validate()

        return res
