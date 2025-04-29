from odoo import models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    check_stock = fields.Boolean('Check Stock', default=False)

    def action_confirm(self):
        for order in self:
            if order.check_stock:
                # Loop through the order lines and check stock
                for line in order.order_line:
                    product = line.product_id
                    qty_to_deliver = line.product_uom_qty

                    # Get stock quantity from the 'khoud/Stock' location
                    khoud_stock = self._get_stock_quantity(product, 'khoud')
                    if khoud_stock >= qty_to_deliver:
                        # Create picking for `khoud/Stock` if enough stock is available
                        self._create_stock_picking(order, product, qty_to_deliver, 'khoud')
                    else:
                        # Allocate remaining quantity from `bawshar/Stock`
                        remaining_qty = qty_to_deliver - khoud_stock
                        if remaining_qty > 0:
                            # Create picking for `bawshar/Stock` for the remaining quantity
                            self._create_stock_picking(order, product, remaining_qty, 'bawshar')

            # Call the original `action_confirm` method to confirm the order
            super(SaleOrder, self).action_confirm()

    def _get_stock_quantity(self, product, location_name):
        location = self.env['stock.location'].search([('name', '=', location_name)], limit=1)
        if not location:
            raise UserError(f"Location {location_name} not found.")

        stock_quant = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id)
        ], limit=1)
        return stock_quant.quantity if stock_quant else 0.0

    def _create_stock_picking(self, order, product, qty, location_name):
        location = self.env['stock.location'].search([('name', '=', location_name)], limit=1)
        if not location:
            raise UserError(f"Location {location_name} not found.")

        # Create stock picking based on the sale order
        picking = self.env['stock.picking'].create({
            'origin': order.name,
            'partner_id': order.partner_id.id,
            'picking_type_id': self._get_picking_type_id(location_name),
            'location_id': location.id,
            'location_dest_id': self._get_destination_location_id(),
            'move_lines': [(0, 0, {
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

    def _get_picking_type_id(self, location_name):
        # Logic to get the appropriate picking type based on location name
        if location_name == 'khoud':
            return self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id
        return self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id

    def _get_destination_location_id(self):
        # Logic to get the destination location (e.g., customer location)
        return self.env['stock.location'].search([('usage', '=', 'customer')], limit=1).id
