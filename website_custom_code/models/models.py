# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_visible = fields.Boolean('Visible', compute='_compute_product_visibility')

    @api.depends('product_variant_ids.internal_qty_available', 'product_variant_ids.hide_on_website')
    def _compute_product_visibility(self):
        for product_temp in self:
            variants = product_temp.product_variant_ids
            is_visible = False in variants.mapped('hide_on_website')
            product_temp.is_visible = is_visible
            if all(v.internal_qty_available == 0 for v in variants):
                product_temp.is_published = is_visible

    def get_possible_combinations_available(self):
        for tpl in self.sudo():
            valid_combination_list = []

            combinations = tpl._get_possible_combinations()
            for cmb in combinations:
                variant = tpl._get_variant_for_combination(cmb)
                if variant.internal_qty_available > 0:
                    available = [item.id for item in cmb]
                    valid_combination_list.append(available)

            return {
                'success': True,
                'message': f'print value_to_show_tuple {valid_combination_list}',
                "value_to_show_tuple": valid_combination_list
            }

    def get_variant_count(self):
        for rec in self:
            valid_combination_list = []
            attribute_ids = []
            attribute_display_types = {}
            unavailable_variant_view_type = []

            all_empty = False
            try:
                iterable = rec.with_context(special_call=True)._get_possible_combinations()
                first = next(iterable)
            except StopIteration:
                all_empty = True

            combinations = (rec._get_possible_combinations() if all_empty else rec.with_context(
                special_call=True)._get_possible_combinations())

            for v in combinations:
                val = []
                for value in v:
                    val.append(value.id)
                    if value.attribute_id.id not in attribute_ids:
                        attribute_ids.append(value.attribute_id.id)
                        attribute_display_types.update({value.attribute_id.id: value.attribute_id.display_type})
                        unavailable_variant_view_type.append(value.attribute_id.unavailable_value_view_type)

                # Get the matching variant for the combination
                variant = rec._get_variant_for_combination(v)

                if variant and variant.internal_qty_available > 0 and not variant.hide_on_website:
                    valid_combination_list.append(tuple(val))

            valid_comb = set(valid_combination_list)
            value_count_per_attr = []
            attribute_line_ids = rec.attribute_line_ids
            if attribute_line_ids:
                for line in attribute_line_ids:
                    value_count_per_attr.append(len(line.value_ids))

            j = 0
            available_variant_values_ids = {}
            all_val = []
            for item in list(valid_comb):
                all_val.extend(list(item))
                available_variant_values_ids[j] = list(item)
                j += 1
            all_val = list(set(all_val))

            variant_val_child_dict = {}
            for i in range(len(all_val)):
                all_child_items = []
                for item in list(valid_comb):
                    items = list(item)
                    try:
                        offset = items.index(all_val[i])
                    except ValueError:
                        offset = -1
                    if offset == -1:
                        continue
                    child_item = []
                    for j in range(offset, len(items)):
                        child_item.append(items[j])
                    all_child_items.extend(child_item)
                child_list = list(set(all_child_items))
                variant_val_child_dict[all_val[i]] = child_list

            unavailable_variant_dict = {
                "attribute_ids": attribute_ids,
                "attribute_display_types": attribute_display_types,
                "unavailable_variant_view_type": unavailable_variant_view_type,
                "value_to_show": variant_val_child_dict,
                "value_to_show_tuple": list(valid_comb),
                "value_count_per_attr": value_count_per_attr
            }
            return unavailable_variant_dict


class ProductProduct(models.Model):
    _inherit = "product.product"

    hide_on_website = fields.Boolean("Hide on Website", help="Check to hide this variant on the website")
    is_out_of_stock = fields.Boolean(compute='_compute_out_of_stock')
    internal_qty_available = fields.Float(string="Qty in Internal Locations", compute="_compute_internal_qty")

    def _compute_out_of_stock(self):
        for rec in self:
            if rec.type == 'product':
                rec.is_out_of_stock = rec.internal_qty_available == 0
                rec.hide_on_website = rec.internal_qty_available == 0
            else:
                rec.is_out_of_stock = False
                rec.hide_on_website = False

    def _compute_internal_qty(self):
        StockQuant = self.env['stock.quant']
        internal_locations = self.env['stock.location'].search([('usage', '=', 'internal')]).ids
        for product in self:
            qty = StockQuant.sudo().read_group(
                domain=[('product_id', '=', product.id), ('location_id', 'in', internal_locations)],
                fields=['quantity:sum'],
                groupby=[]
            )
            product.internal_qty_available = qty[0]['quantity'] if qty else 0.0


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    unavailable_value_view_type = fields.Selection([
        ('none', 'None'),
        ('hide', 'Hide')
    ], default='none', string='Unavailable Variant View Type')
