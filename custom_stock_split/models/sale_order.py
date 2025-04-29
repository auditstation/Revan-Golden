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
                        self._create_stock_picking(order, product, qty_to_deliver, 8)
                    else:
                        # Allocate remaining quantity from `bawshar/Stock` (ID: 18)
                        remaining_qty = qty_to_deliver - khoud_stock
                        if remaining_qty > 0:
                            # Create picking for `bawshar/Stock` for the remaining quantity
                            self._create_stock_picking(order, product, remaining_qty, 18)

            # Call the original `action_confirm` method to confirm the order
            super(SaleOrder, self).action_confirm()

    def _get_stock_quantity(self, product, location_id):
        stock_quant = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location_id)
        ], limit=1)
        return stock_quant.quantity if stock_quant else 0.0

    def _create_stock_picking(self, order, product, qty, location_id):
        location = self.env['stock.location'].browse(location_id)
        if not location:
            raise UserError(f"Location with ID {location_id} not found.")

        picking = self.env['stock.picking'].create({
            'origin': order.name,
            'partner_id': order.partner_id.id,
            'picking_type_id': self._get_picking_type_id(location_id),
            'location_id': location.id,
            'location_dest_id': self._get_destination_location_id(),
            'move_ids_without_package': [(0, 0, {
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': qty,
                'name': product.name,
                'location_id': location.id,
                'location_dest_id': self._get_destination_location_id(),
            })],
        })
        picking.action_confirm()
        picking.action_assign()

    def _get_picking_type_id(self, location_id):
        # Logic to get the appropriate picking type based on location ID
        if location_id == 8:  # khoud location ID
            return self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id
        elif location_id == 18:  # bawshar location ID
            return self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id
        return self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id

    def _get_destination_location_id(self):
        # Logic to get the destination location (e.g., customer location)
        return self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id
