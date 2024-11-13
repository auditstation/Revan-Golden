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
#     @http.route("/get_product_variant_data_website", type="json", website=True, auth="public", methods=["POST"])
#     def get_product_variant_data(self, product_tmpl_id):
    @http.route('/get_product_variant_data_website', type='json', auth='public', methods=['POST'], csrf=False)
    def get_product_variant_data(self):
    # Access the JSON data sent in the request
        product_tmpl_id = http.request.jsonrequest.get('product_tmpl_id')

        product_tmpl_id = request.env["product.template"].search([("id", "=", int(product_tmpl_id))])
        if product_tmpl_id:
            return product_tmpl_id.get_possible_combinations_available()
        if not product_tmpl_id:
            return {
                'error': True,
                'message': 'Product Template ID is missingsss'
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
