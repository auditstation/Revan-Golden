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
        product = request.env["product.template"].browse(int(product_tmpl_id))
        if product.exists():
            value_to_show_tuple = product.get_variant_count()
            return {"value_to_show_tuple": value_to_show_tuple}
        return {"error": "Product not found or no variants available"}
