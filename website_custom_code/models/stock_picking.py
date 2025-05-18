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
    #                 ('state', 'not in', ['done', 'cancel']),
    #             ], order='id ASC')
    #
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
        res = super(StockPicking, self).button_validate()

        for picking in self:
            if picking.picking_type_id.code == 'internal' and picking.sale_id:
                # Find all delivery pickings related to the same sale order
                delivery_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),
                    ('picking_type_id.code', '=', 'outgoing'),
                    ('state', 'not in', ['done', 'cancel']),
                ], order='id ASC')

                for delivery_picking in delivery_pickings:
                    # Set quantity done to match the demand for validation
                    for move in delivery_picking.move_ids_without_package:
                        move.quantity_done = move.product_uom_qty

                    # Reserve stock if needed
                    delivery_picking.action_assign()

                    # Validate the delivery
                    delivery_picking.button_validate()

        return res