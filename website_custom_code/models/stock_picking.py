from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def button_validate(self):
    #     res = super(StockPicking,self).button_validate()
    #
    #     for picking in self:
    #         if picking.picking_type_id.code == 'internal' and picking.sale_id:
    #             delivery_pickings = self.env['stock.picking'].search([
    #                 ('sale_id', '=', picking.sale_id.id),
    #                 ('picking_type_id.code', '=', 'outgoing'),
    #             ])
    #             if delivery_pickings:
    #                 for delivery_picking in delivery_pickings:
    #                     for move in delivery_picking.move_ids_without_package:
    #                         move.quantity  = move.product_uom_qty
    #                     delivery_picking.action_assign()
    #                     delivery_picking.button_validate()
    #
    #     return res
    #
    #

    def button_validate(self):
        for picking in self:
            # If it's an internal picking linked to a sale
            if picking.picking_type_id.code == 'internal' and picking.sale_id:
                # First handle outgoing delivery
                delivery_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),
                    ('picking_type_id.code', '=', 'outgoing'),
                    ('state', 'not in', ['done', 'cancel']),
                ])
                for delivery_picking in delivery_pickings:
                    for move in delivery_picking.move_ids_without_package:
                        move.quantity = move.product_uom_qty
                    delivery_picking.action_assign()
                    delivery_picking.button_validate()

        # Now proceed with the original validation
        return super(StockPicking, self).button_validate()