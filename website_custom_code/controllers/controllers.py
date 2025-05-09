# -*- coding: utf-8 -*-

# from odoo import http, _
# from odoo.exceptions import UserError
# from odoo.http import request


# class HideVariant(http.Controller):
#     @http.route("/get_product_variant_data_website", type="json", website=True, auth="public")
#     def get_product_variant_data(self, product_tmpl_id):
#         product_tmpl_id = request.env["product.template"].search([("id", "=", product_tmpl_id)])
#         if product_tmpl_id:
#             return product_tmpl_id.get_possible_combinations_available()
from odoo import http
from odoo.http import request


class HideVariant(http.Controller):
    @http.route("/get_product_variant_data_website", type="json", website=True, auth="public", methods=["POST"])
    def get_product_variant_data(self, product_tmpl_id):

        product_tmpl_id = request.env["product.template"].search([("id", "=", int(product_tmpl_id))])
        if product_tmpl_id:
            return {
                'success': True,
                'message': 'Product found successfullysssssssssss',
                'data': product_tmpl_id.get_possible_combinations_available()
            }
            # return product_tmpl_id.get_possible_combinations_available()
        if not product_tmpl_id:
            return {
                'error': True,
                'message': 'Product Template ID is missing'
            }






        # try:
        #     # Convert the ID to an integer and fetch the product template
        #     product_tmpl_id = int(product_tmpl_id)
        #     product = request.env["product.template"].browse(product_tmpl_id)
        #
        #     if not product.exists():
        #         return {
        #             'error': True,
        #             'message': 'Product not found'
        #         }
        #
        #     # Fetch the variant count or other data
        #     value_to_show_tuple = product.get_variant_count()
        #
        #     # Return the expected structure
        #     return {
        #         'error': False,
        #         'value_to_show_tuple': value_to_show_tuple
        #     }
        # except Exception as e:
        #     return {
        #         'error': True,
        #         'message': f'Odoo Server Error: {str(e)}'
        #     }

    # @http.route("/get_variant_quantities", type="json", website=True, auth="public", methods=["POST"])
    # def get_variant_quantities(self, product_tmpl_id):
    #     product_tmpl = request.env["product.template"].sudo().browse(int(product_tmpl_id))
    #
    #     if not product_tmpl:
    #         return {
    #             'error': True,
    #             'message': 'Product Template not found'
    #         }
    #
    #     # Get all warehouses
    #     warehouses = request.env['stock.warehouse'].sudo().search([])
    #
    #     # Get website warehouse if configured
    #     website = request.website
    #     website_warehouse_id = website.warehouse_id.id if website.warehouse_id else False
    #
    #     result = {}
    #
    #     # For each variant, get quantities across warehouses
    #     for variant in product_tmpl.product_variant_ids:
    #         variant_data = {
    #             'variant_id': variant.id,
    #             'variant_name': variant.display_name,
    #             'attribute_values': [(attr.attribute_id.name, attr.name) for attr in variant.product_template_attribute_value_ids],
    #             'warehouses': {},
    #             'total_qty': 0
    #         }
    #
    #         # Get quantity for each warehouse
    #         for warehouse in warehouses:
    #             qty = variant.with_context(warehouse=warehouse.id).qty_available
    #             variant_data['warehouses'][warehouse.name] = qty
    #             variant_data['total_qty'] += qty
    #
    #             # Mark if this is the website warehouse
    #             if warehouse.id == website_warehouse_id:
    #                 variant_data['warehouses'][warehouse.name + ' (Website Warehouse)'] = qty
    #
    #         result[variant.id] = variant_data
    #
    #     return result