# -*- coding: utf-8 -*-
# from odoo import http


# class MantainceReportSales(http.Controller):
#     @http.route('/mantaince_report_sales/mantaince_report_sales', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mantaince_report_sales/mantaince_report_sales/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mantaince_report_sales.listing', {
#             'root': '/mantaince_report_sales/mantaince_report_sales',
#             'objects': http.request.env['mantaince_report_sales.mantaince_report_sales'].search([]),
#         })

#     @http.route('/mantaince_report_sales/mantaince_report_sales/objects/<model("mantaince_report_sales.mantaince_report_sales"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mantaince_report_sales.object', {
#             'object': obj
#         })
