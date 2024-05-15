# -*- coding: utf-8 -*-
import json

from odoo import models, fields,api
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_visible = fields.Boolean('Visible', compute='_compute_product_visibility')
    @api.depends('qty_available')
    def _compute_product_visibility(self):
        for product_temp in self:
            
                variants = product_temp.product_variant_ids
                is_visible = False in product_temp.product_variant_ids.mapped('hide_on_website')
                product_temp.is_visible = is_visible
                if product_temp.qty_available == 0:
                    product_temp.is_published = is_visible

    def get_possible_combinations_available(self):

        for tpl in self.sudo():
            valid_combination_list = []

            combinations = tpl._get_possible_combinations()

            for cmb in combinations:
                variant = tpl._get_variant_for_combination(cmb)

                if variant.qty_available > 0:
                    available = list(map(lambda item: item.id, cmb))
                    valid_combination_list.append(available)

            return {
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
            if all_empty:
                for v in rec._get_possible_combinations():
                    val = []
                    for value in v:
                        val.append(value.id)
                        if value.attribute_id.id not in attribute_ids:
                            attribute_ids.append(value.attribute_id.id)
                            attribute_display_types.update({value.attribute_id.id: value.attribute_id.display_type})
                            unavailable_variant_view_type.append(value.attribute_id.unavailable_value_view_type)
            else:
                for v in rec.with_context(special_call=True)._get_possible_combinations():
                    val = []
                    for value in v:
                        val.append(value.id)
                        if value.attribute_id.id not in attribute_ids:
                            attribute_ids.append(value.attribute_id.id)
                            attribute_display_types.update({value.attribute_id.id: value.attribute_id.display_type})
                            unavailable_variant_view_type.append(value.attribute_id.unavailable_value_view_type)

                    valid_combination_list.append(tuple(val))

            valid_comb = set(valid_combination_list)
            value_count_per_attr = []
            attribute_line_ids = self.attribute_line_ids
            if attribute_line_ids:
                for line in attribute_line_ids:
                    value_count_per_attr.append(len(line.value_ids))
            j = 0
            available_variant_values_ids = {}
            all_val = []
            for item in list(valid_comb):
                all_val.extend(list(item))
                available_variant_values_ids[j] = (list(item))
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
            unavailable_variant_dict = {"attribute_ids": attribute_ids,
                                        "attribute_display_types": attribute_display_types,
                                        "unavailable_variant_view_type": unavailable_variant_view_type,
                                        "value_to_show": variant_val_child_dict,
                                        "value_to_show_tuple": list(valid_comb),
                                        "value_count_per_attr": value_count_per_attr}
            return unavailable_variant_dict

    def _get_first_possible_combination(self, parent_combination=None, necessary_values=None):
        """See `_get_possible_combinations` (one iteration).

        This method return the same result (empty recordset) if no
        combination is possible at all which would be considered a negative
        result, or if there are no attribute lines on the template in which
        case the "empty combination" is actually a possible combination.
        Therefore the result of this method when empty should be tested
        with `_is_combination_possible` if it's important to know if the
        resulting empty combination is actually possible or not.
        """

        com = next(self._get_possible_combinations(parent_combination, necessary_values),
                   self.env['product.template.attribute.value'])
        no_variant_attr_val = self.env['product.template.attribute.value']
        for ptav in com:
            if ptav.attribute_id.create_variant == "no_variant":
                no_variant_attr_val += ptav

        for combination in self._get_possible_combinations(parent_combination, necessary_values):
            
            org_combination = combination
            combination -= no_variant_attr_val
            # variant_id = self.product_variant_ids.filtered(
            #     lambda variant: variant.product_template_attribute_value_ids == combination)
            variant_id = self._get_variant_for_combination(combination)
           
            if variant_id and not variant_id.hide_on_website:
                

                return org_combination
            elif variant_id.product_tmpl_id.qty_available == 0:
                return org_combination
           

    def _is_combination_possible(self, combination, parent_combination=None, ignore_no_variant=False):
        result = super(ProductTemplate, self)._is_combination_possible(combination, parent_combination,
                                                                       ignore_no_variant)
        if result and self._context.get("special_call"):
            no_variant_attr_val = self.env['product.template.attribute.value']

            for ptav in combination:
                if ptav.attribute_id.create_variant == "no_variant":
                    no_variant_attr_val += ptav
            combination -= no_variant_attr_val
            # variant_id = self.product_variant_ids.filtered(
            #     lambda variant: variant.product_template_attribute_value_ids == combination)
            variant_id = self._get_variant_for_combination(combination)
            if variant_id and self._context.get("special_call"):
                if variant_id.hide_on_website:
                    return False
                else:
                    return True
        return result

    # warlock fixing
    def _get_variant_for_combination(self, combination):
        if not combination:
            combination = self.env['product.template.attribute.value']

        return super(ProductTemplate, self)._get_variant_for_combination(combination)

class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    unavailable_value_view_type = fields.Selection([('none', 'None'), ('hide', 'Hide')], default='none',
                                                   string='Unavailable Variant View Type')


class ProductProduct(models.Model):
    _inherit = "product.product"

    hide_on_website = fields.Boolean("Hide on Website",
                                     help="Check right if you want to hide the variant in your website")
    is_out_of_stock = fields.Boolean(compute='_compute_out_of_stock')

    def _compute_out_of_stock(self):
        for rec in self:
            if rec.type == 'product':
                rec.is_out_of_stock = rec.qty_available == 0
                rec.hide_on_website = rec.qty_available == 0

            else:
                rec.is_out_of_stock = False
                rec.hide_on_website = False
