from odoo import models
from odoo.exceptions import UserError

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
    #                         move.quantity  += move.product_uom_qty
    #                     delivery_picking.action_assign()
    #                     delivery_picking.button_validate()
    #
    #     return res

    def button_validate(self):
        for picking in self:
            # If the current picking is a delivery
            if picking.picking_type_id.code == 'outgoing' and picking.sale_id:
                # Search for related internal pickings that are not done
                internal_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),
                    ('picking_type_id.code', '=', 'internal'),
                    ('state', 'not in', ['done', 'cancel']),
                ])
                if internal_pickings:
                    # internal_pickings.action_assign()
                    internal_pickings.button_validate()

            # If current picking is internal and linked to sale, validate deliveries afterwards
            elif picking.picking_type_id.code == 'internal' and picking.sale_id:
                res = super(StockPicking, self).button_validate()

                delivery_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),
                    ('picking_type_id.code', '=', 'outgoing'),
                    ('state', 'not in', ['done', 'cancel']),
                ])

                for delivery_picking in delivery_pickings:
                    if delivery_picking.move_ids_without_package:
                        for move in delivery_picking.move_ids_without_package:
                            move.quantity += move.product_uom_qty
                        delivery_picking.action_assign()
                        delivery_picking.button_validate()

                return res

        return super(StockPicking, self).button_validate()