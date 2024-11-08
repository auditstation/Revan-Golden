/** @odoo-module **/

import { ajax } from '@web/core/ajax';
import publicWidget from 'web.public.widget';

let id_tuples = undefined;

publicWidget.registry.WebsiteSale = publicWidget.registry.WebsiteSale.extend({

    async willStart() {
        await this._super(...arguments);
        const $parent = $('.js_product');
        const product_tmpl_id = parseInt($parent.find('.product_template_id').val());
        if (product_tmpl_id) {
            const data = await ajax.rpc('/get_product_variant_data', {
                'product_tmpl_id': product_tmpl_id,
            });
            id_tuples = data;
        }
    },

    onChangeVariant(ev) {
        const $parent = $(ev.target).closest('.js_product');
        const $target = $(ev.target);

        if (!$parent.length || !id_tuples) {
            return;
        }

        if ($target.is('input[type=radio]') && $target.is(':checked')) {
            this._hideVariants($target, $parent);
        } else {
            $parent.find("input:checked").each((index, element) => {
                this._hideVariants($(element), $parent);
            });
        }

        this._super.apply(this, arguments);
    },

    _hideVariants($target, $parent) {
        const $variantContainer = $target.closest('ul').closest('li');
        const currentSelect = $variantContainer.attr('data-attribute_name');

        if (currentSelect === 'SIZE') return;

        $parent.find(`li[data-attribute_name!='${currentSelect}'][data-attribute_display_type='radio']`)
            .each(function () {
                const $current = $(this);
                let firstShowed = null;
                let anyChecked = false;

                $current.find("input[type=radio]").each(function () {
                    const input = $(this);
                    const found = id_tuples.value_to_show_tuple.find(el => {
                        const tupla = JSON.stringify(el);
                        const t1 = JSON.stringify([parseInt($target.val()), parseInt(input.val())]);
                        const t2 = JSON.stringify([parseInt(input.val()), parseInt($target.val())]);
                        return tupla === t1 || tupla === t2;
                    });
                    if (!found) {
                        input.parent().hide();
                        input.prop("checked", false);
                    } else {
                        input.parent().show();
                        if (!firstShowed) firstShowed = input;
                        if (!anyChecked) anyChecked = input.is(":checked");
                    }
                });

                if (!anyChecked && firstShowed) {
                    firstShowed.prop("checked", true);
                }
            });
    }
});
