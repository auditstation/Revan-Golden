from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    check_stock = fields.Boolean(string='Check Stock', compute='_compute_check_stock', store=True)

    @api.depends('website_id')
    def _compute_check_stock(self):
        for order in self:
            order.check_stock = order.website_id



    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.check_stock:
                # Loop through the order lines and check stock
                for line in order.order_line:
                    product = line.product_id
                    qty_to_deliver = line.product_uom_qty

                    # Get stock quantity from the 'khoud/Stock' location (ID: 8)
                    khoud_stock = self._get_stock_quantity(product, 8)  # ID for khoud
                    if khoud_stock >= qty_to_deliver:
                        # Create picking for `khoud/Stock` if enough stock is available
                        if order.picking_ids:
                            for picking in order.picking_ids:
                                if picking.picking_type_id.code == 'outgoing':
                                    for move in picking.move_ids_without_package:
                                        if product.id == move.product_id.id:
                                            move.quantity  = move.product_uom_qty


                        # self._create_stock_picking(order, product, qty_to_deliver, 8)
                    else:
                        # Allocate remaining quantity from `bawshar/Stock` (ID: 18)
                        remaining_qty = qty_to_deliver - khoud_stock
                        if remaining_qty > 0:
                            if order.picking_ids:
                                for picking in order.picking_ids:
                                    if picking.picking_type_id.code == 'outgoing':
                                        for move in picking.move_ids_without_package:
                                            if product.id == move.product_id.id:
                                                move.quantity  = move.product_uom_qty
                                        picking.state="waiting"
                                    if picking.picking_type_id.code == 'internal':
                                        for move in picking.move_ids_without_package:
                                            if product.id == move.product_id.id:

                                                move.quantity  = remaining_qty
                                                move.product_uom_qty = remaining_qty


                            # Create picking for `bawshar/Stock` for the remaining quantity
                            # self._create_stock_picking(order, product, remaining_qty, 18)

        # Call the original `action_confirm` method to confirm the order
        return res

    def _get_stock_quantity(self, product, location_id):
        stock_quant = self.env['stock.quant'].sudo().search([
            ('product_id', '=', product.id),
            ('location_id', '=', location_id)
        ], limit=1)
        return stock_quant.quantity if stock_quant else 0.0




