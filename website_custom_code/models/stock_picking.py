from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking,self).button_validate()

        for picking in self:
            if picking.picking_type_id.code == 'internal' and picking.sale_id:
                delivery_pickings = self.env['stock.picking'].search([
                    ('sale_id', '=', picking.sale_id.id),
                    ('picking_type_id.code', '=', 'outgoing'),
                ])
                if delivery_pickings:
                    for delivery_picking in delivery_pickings:
                        delivery_picking.state='assigned'

        return res
